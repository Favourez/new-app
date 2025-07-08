#!/usr/bin/env python3
"""
AI Resume Parser Training System
===============================

This script trains a custom AI model for resume parsing using the generated
synthetic resume dataset.
"""

import json
import re
import random
import numpy as np
import pandas as pd
from collections import defaultdict, Counter
import pickle
import os

# NLP and ML libraries
import spacy
from spacy.training import Example
from spacy.util import minibatch, compounding
import warnings
warnings.filterwarnings("ignore")

class ResumeAnnotator:
    """Create training annotations for resume parsing"""
    
    def __init__(self):
        self.skill_patterns = self.load_skill_patterns()
        self.entity_labels = [
            "PERSON", "EMAIL", "PHONE", "SKILL", "COMPANY", 
            "TITLE", "EDUCATION", "UNIVERSITY", "EXPERIENCE", "CERTIFICATION"
        ]
    
    def load_skill_patterns(self):
        """Load comprehensive skill patterns"""
        skills = [
            # Programming Languages
            'Python', 'JavaScript', 'Java', 'C++', 'C#', 'Go', 'Rust', 'Swift',
            'Kotlin', 'PHP', 'Ruby', 'Scala', 'R', 'MATLAB', 'TypeScript',
            
            # Web Technologies
            'React', 'Angular', 'Vue.js', 'HTML5', 'CSS3', 'Node.js', 'Express',
            'Django', 'Flask', 'Spring Boot', 'Laravel', 'Bootstrap',
            
            # Databases
            'MySQL', 'PostgreSQL', 'MongoDB', 'Redis', 'Elasticsearch',
            'Oracle', 'SQL Server', 'SQLite', 'DynamoDB',
            
            # Cloud & DevOps
            'AWS', 'Azure', 'Google Cloud', 'Docker', 'Kubernetes', 'Jenkins',
            'Terraform', 'Ansible', 'Git', 'CI/CD', 'Linux',
            
            # Data Science
            'Machine Learning', 'Deep Learning', 'TensorFlow', 'PyTorch',
            'Scikit-learn', 'Pandas', 'NumPy', 'Matplotlib', 'Jupyter',
            'Apache Spark', 'Hadoop', 'Tableau', 'Power BI',
            
            # Mobile
            'iOS Development', 'Android Development', 'React Native', 'Flutter',
            
            # Other
            'Microservices', 'REST API', 'GraphQL', 'Blockchain', 'IoT',
            'Agile', 'Scrum', 'Project Management', 'Leadership'
        ]
        
        # Create pattern variations
        patterns = set()
        for skill in skills:
            patterns.add(skill)
            patterns.add(skill.lower())
            patterns.add(skill.upper())
            # Add variations without special characters
            clean_skill = re.sub(r'[^\w\s]', '', skill)
            if clean_skill != skill:
                patterns.add(clean_skill)
        
        return list(patterns)
    
    def annotate_text(self, text, resume_data):
        """Create entity annotations for resume text"""
        
        entities = []
        text_lower = text.lower()
        
        # Annotate person name
        if resume_data['name'] in text:
            start = text.find(resume_data['name'])
            end = start + len(resume_data['name'])
            entities.append((start, end, "PERSON"))
        
        # Annotate email
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        for match in re.finditer(email_pattern, text):
            entities.append((match.start(), match.end(), "EMAIL"))
        
        # Annotate phone
        phone_pattern = r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b'
        for match in re.finditer(phone_pattern, text):
            entities.append((match.start(), match.end(), "PHONE"))
        
        # Annotate skills
        for skill in resume_data['skills']:
            # Find all occurrences of the skill
            skill_lower = skill.lower()
            start_pos = 0
            while True:
                pos = text_lower.find(skill_lower, start_pos)
                if pos == -1:
                    break
                
                # Check if it's a whole word
                if (pos == 0 or not text[pos-1].isalnum()) and \
                   (pos + len(skill) >= len(text) or not text[pos + len(skill)].isalnum()):
                    entities.append((pos, pos + len(skill), "SKILL"))
                
                start_pos = pos + 1
        
        # Annotate companies
        for exp in resume_data['work_experience']:
            company = exp['company']
            if company in text:
                start = text.find(company)
                end = start + len(company)
                entities.append((start, end, "COMPANY"))
        
        # Annotate job titles
        title = resume_data['title']
        if title in text:
            start = text.find(title)
            end = start + len(title)
            entities.append((start, end, "TITLE"))
        
        # Annotate university
        university = resume_data['education']['university']
        if university in text:
            start = text.find(university)
            end = start + len(university)
            entities.append((start, end, "UNIVERSITY"))
        
        # Annotate degree
        degree = resume_data['education']['degree']
        if degree in text:
            start = text.find(degree)
            end = start + len(degree)
            entities.append((start, end, "EDUCATION"))
        
        # Annotate experience years
        exp_pattern = r'\b\d+\s*years?\b'
        for match in re.finditer(exp_pattern, text, re.IGNORECASE):
            entities.append((match.start(), match.end(), "EXPERIENCE"))
        
        # Remove overlapping entities (keep longer ones)
        entities = self.remove_overlapping_entities(entities)
        
        return {"entities": entities}
    
    def remove_overlapping_entities(self, entities):
        """Remove overlapping entity annotations"""
        
        # Sort by start position
        entities.sort(key=lambda x: x[0])
        
        filtered = []
        for entity in entities:
            start, end, label = entity
            
            # Check for overlap with existing entities
            overlap = False
            for existing in filtered:
                ex_start, ex_end, ex_label = existing
                
                # Check if there's overlap
                if not (end <= ex_start or start >= ex_end):
                    # Keep the longer entity
                    if (end - start) <= (ex_end - ex_start):
                        overlap = True
                        break
                    else:
                        # Remove the shorter existing entity
                        filtered.remove(existing)
            
            if not overlap:
                filtered.append(entity)
        
        return filtered
    
    def create_training_data(self, resumes, resume_texts):
        """Create training data from resume dataset"""
        
        print("📝 Creating training annotations...")
        
        training_data = []
        
        for i, (resume, text) in enumerate(zip(resumes, resume_texts)):
            if (i + 1) % 200 == 0:
                print(f"Annotated {i + 1}/{len(resumes)} resumes...")
            
            try:
                annotations = self.annotate_text(text, resume)
                training_data.append((text, annotations))
            except Exception as e:
                print(f"Error annotating resume {i+1}: {e}")
                continue
        
        print(f"✅ Created {len(training_data)} training examples")
        return training_data

class ResumeParserTrainer:
    """Train custom NER model for resume parsing"""
    
    def __init__(self):
        self.nlp = None
        self.model_path = "resume_parser_model"
    
    def create_model(self, training_data):
        """Create and train spaCy NER model"""
        
        print("🏗️ Creating spaCy NER model...")
        
        # Create blank English model
        self.nlp = spacy.blank("en")
        
        # Add NER pipeline
        ner = self.nlp.add_pipe("ner")
        
        # Add entity labels
        labels = ["PERSON", "EMAIL", "PHONE", "SKILL", "COMPANY", 
                 "TITLE", "EDUCATION", "UNIVERSITY", "EXPERIENCE", "CERTIFICATION"]
        
        for label in labels:
            ner.add_label(label)
        
        # Convert training data to spaCy format
        examples = []
        for text, annotations in training_data:
            try:
                doc = self.nlp.make_doc(text)
                example = Example.from_dict(doc, annotations)
                examples.append(example)
            except Exception as e:
                continue
        
        print(f"📊 Training with {len(examples)} examples...")
        
        # Initialize the model
        self.nlp.initialize(lambda: examples)
        
        # Training loop
        for epoch in range(30):
            print(f"Epoch {epoch + 1}/30")
            
            random.shuffle(examples)
            losses = {}
            
            # Create mini-batches
            batches = minibatch(examples, size=compounding(4.0, 32.0, 1.001))
            
            for batch in batches:
                self.nlp.update(batch, losses=losses)
            
            if (epoch + 1) % 5 == 0:
                print(f"  Losses: {losses}")
        
        print("✅ Model training completed!")
        
        return self.nlp
    
    def save_model(self):
        """Save trained model"""
        if self.nlp:
            self.nlp.to_disk(self.model_path)
            print(f"💾 Model saved to '{self.model_path}'")
    
    def load_model(self):
        """Load trained model"""
        if os.path.exists(self.model_path):
            self.nlp = spacy.load(self.model_path)
            print(f"📂 Model loaded from '{self.model_path}'")
            return self.nlp
        else:
            print(f"❌ Model not found at '{self.model_path}'")
            return None
    
    def evaluate_model(self, test_data):
        """Evaluate model performance"""
        
        if not self.nlp:
            print("❌ No model loaded for evaluation")
            return
        
        print("📈 Evaluating model performance...")
        
        correct = 0
        total = 0
        entity_stats = defaultdict(lambda: {'correct': 0, 'total': 0, 'predicted': 0})
        
        for text, annotations in test_data[:100]:  # Evaluate on subset
            doc = self.nlp(text)
            predicted_entities = [(ent.start_char, ent.end_char, ent.label_) for ent in doc.ents]
            true_entities = annotations['entities']
            
            # Count entity-level accuracy
            for pred in predicted_entities:
                entity_stats[pred[2]]['predicted'] += 1
                if pred in true_entities:
                    entity_stats[pred[2]]['correct'] += 1
                    correct += 1
                total += 1
            
            for true in true_entities:
                entity_stats[true[2]]['total'] += 1
        
        # Calculate metrics
        overall_precision = correct / total if total > 0 else 0
        
        print(f"\n📊 Evaluation Results:")
        print(f"Overall Precision: {overall_precision:.3f}")
        print(f"Total Predictions: {total}")
        print(f"Correct Predictions: {correct}")
        
        print(f"\n📋 Per-Entity Performance:")
        for entity, stats in entity_stats.items():
            precision = stats['correct'] / stats['predicted'] if stats['predicted'] > 0 else 0
            recall = stats['correct'] / stats['total'] if stats['total'] > 0 else 0
            f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
            
            print(f"  {entity}:")
            print(f"    Precision: {precision:.3f}")
            print(f"    Recall: {recall:.3f}")
            print(f"    F1-Score: {f1:.3f}")

class ResumeParser:
    """Production resume parser using trained model"""
    
    def __init__(self, model_path="resume_parser_model"):
        self.model_path = model_path
        self.nlp = None
        self.load_model()
    
    def load_model(self):
        """Load the trained model"""
        try:
            self.nlp = spacy.load(self.model_path)
            print(f"✅ Resume parser model loaded successfully")
        except Exception as e:
            print(f"❌ Error loading model: {e}")
    
    def parse_resume(self, text):
        """Parse resume text and extract information"""
        
        if not self.nlp:
            return {"error": "Model not loaded"}
        
        doc = self.nlp(text)
        
        # Extract entities
        entities = {
            'names': [],
            'emails': [],
            'phones': [],
            'skills': [],
            'companies': [],
            'titles': [],
            'education': [],
            'universities': [],
            'experience': [],
            'certifications': []
        }
        
        entity_mapping = {
            'PERSON': 'names',
            'EMAIL': 'emails',
            'PHONE': 'phones',
            'SKILL': 'skills',
            'COMPANY': 'companies',
            'TITLE': 'titles',
            'EDUCATION': 'education',
            'UNIVERSITY': 'universities',
            'EXPERIENCE': 'experience',
            'CERTIFICATION': 'certifications'
        }
        
        for ent in doc.ents:
            if ent.label_ in entity_mapping:
                entities[entity_mapping[ent.label_]].append(ent.text.strip())
        
        # Remove duplicates and clean
        for key in entities:
            entities[key] = list(set(entities[key]))
        
        # Extract structured information
        parsed_data = {
            'name': entities['names'][0] if entities['names'] else '',
            'email': entities['emails'][0] if entities['emails'] else '',
            'phone': entities['phones'][0] if entities['phones'] else '',
            'skills': entities['skills'],
            'companies': entities['companies'],
            'job_titles': entities['titles'],
            'education': entities['education'],
            'universities': entities['universities'],
            'experience_mentions': entities['experience'],
            'certifications': entities['certifications'],
            'total_entities_found': len(doc.ents)
        }
        
        return parsed_data
    
    def parse_resume_file(self, file_path):
        """Parse resume from file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
            return self.parse_resume(text)
        except Exception as e:
            return {"error": f"Error reading file: {e}"}

def main():
    """Main training pipeline"""
    
    print("🚀 AI Resume Parser Training Pipeline")
    print("=" * 50)
    
    # Load generated dataset
    print("📂 Loading resume dataset...")
    
    try:
        with open('resume_dataset/resumes_structured.json', 'r') as f:
            resumes = json.load(f)
        
        with open('resume_dataset/resumes_text.txt', 'r') as f:
            content = f.read()
            resume_texts = content.split('=== RESUME ')[1:]  # Skip first empty split
            resume_texts = [text.split('===\n')[1].strip() for text in resume_texts]
        
        print(f"✅ Loaded {len(resumes)} resumes")
        
    except FileNotFoundError:
        print("❌ Resume dataset not found. Please run 'python resume_generator.py' first.")
        return
    
    # Create annotations
    annotator = ResumeAnnotator()
    training_data = annotator.create_training_data(resumes, resume_texts)
    
    # Split data
    split_idx = int(0.8 * len(training_data))
    train_data = training_data[:split_idx]
    test_data = training_data[split_idx:]
    
    print(f"📊 Training set: {len(train_data)} examples")
    print(f"📊 Test set: {len(test_data)} examples")
    
    # Train model
    trainer = ResumeParserTrainer()
    model = trainer.create_model(train_data)
    
    # Evaluate model
    trainer.evaluate_model(test_data)
    
    # Save model
    trainer.save_model()
    
    # Test the parser
    print("\n🧪 Testing the trained parser...")
    parser = ResumeParser()
    
    # Test with a sample resume
    if resume_texts:
        sample_text = resume_texts[0]
        result = parser.parse_resume(sample_text)
        
        print(f"\n📄 Sample Parse Result:")
        print(f"Name: {result['name']}")
        print(f"Email: {result['email']}")
        print(f"Skills: {result['skills'][:5]}...")  # Show first 5 skills
        print(f"Companies: {result['companies']}")
        print(f"Total entities found: {result['total_entities_found']}")
    
    print("\n🎉 Training completed successfully!")
    print("✅ Model saved and ready for use")
    print("📝 Use ResumeParser class to parse new resumes")

if __name__ == "__main__":
    main()
