const express = require('express');
const cors = require('cors');
const multer = require('multer');
const nodemailer = require('nodemailer');
require('dotenv').config();

const app = express();
const PORT = process.env.PORT || 5000;

// Middleware
app.use(cors());
app.use(express.json());

// Configure multer for file uploads
const storage = multer.memoryStorage();
const upload = multer({ 
  storage,
  limits: {
    fileSize: 5 * 1024 * 1024 // 5MB limit
  },
  fileFilter: (req, file, cb) => {
    if (file.mimetype === 'application/pdf') {
      cb(null, true);
    } else {
      cb(new Error('Only PDF files are allowed'), false);
    }
  }
});

// Email configuration
const transporter = nodemailer.createTransporter({
  service: 'gmail',
  auth: {
    user: process.env.EMAIL_USER,
    pass: process.env.EMAIL_PASS
  }
});

// Routes
app.get('/', (req, res) => {
  res.json({ message: 'Job Portal API Server' });
});

// Resume parsing endpoint
app.post('/api/parse-resume', upload.single('resume'), async (req, res) => {
  try {
    if (!req.file) {
      return res.status(400).json({ error: 'No file uploaded' });
    }

    // Simplified resume parsing (in production, use a proper parsing service)
    const mockParsedData = {
      skills: ['JavaScript', 'React', 'Node.js', 'Python', 'SQL', 'Git'],
      experience: '3+ years of software development experience',
      education: 'Bachelor of Science in Computer Science',
      contact: {
        email: 'extracted@email.com',
        phone: '+1234567890'
      }
    };

    res.json({
      success: true,
      data: mockParsedData
    });
  } catch (error) {
    console.error('Resume parsing error:', error);
    res.status(500).json({ error: 'Failed to parse resume' });
  }
});

// Send application email
app.post('/api/send-application-email', async (req, res) => {
  try {
    const { 
      applicantEmail, 
      applicantName, 
      jobTitle, 
      companyName, 
      compatibilityScore 
    } = req.body;

    const mailOptions = {
      from: process.env.EMAIL_USER,
      to: applicantEmail,
      subject: `Application Confirmation - ${jobTitle}`,
      html: `
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
          <h2 style="color: #2563eb;">Application Submitted Successfully!</h2>
          
          <p>Dear ${applicantName},</p>
          
          <p>Thank you for applying to the position of <strong>${jobTitle}</strong> at <strong>${companyName}</strong>.</p>
          
          <div style="background-color: #f3f4f6; padding: 20px; border-radius: 8px; margin: 20px 0;">
            <h3 style="margin-top: 0;">Application Details:</h3>
            <ul style="list-style: none; padding: 0;">
              <li><strong>Position:</strong> ${jobTitle}</li>
              <li><strong>Company:</strong> ${companyName}</li>
              <li><strong>Compatibility Score:</strong> ${compatibilityScore}%</li>
              <li><strong>Application Date:</strong> ${new Date().toLocaleDateString()}</li>
            </ul>
          </div>
          
          <p>We have received your application and will review it shortly. You will be notified of any updates regarding your application status.</p>
          
          <p>Best regards,<br>The Job Portal Team</p>
          
          <hr style="margin: 30px 0; border: none; border-top: 1px solid #e5e7eb;">
          <p style="font-size: 12px; color: #6b7280;">
            This is an automated email. Please do not reply to this message.
          </p>
        </div>
      `
    };

    await transporter.sendMail(mailOptions);
    
    res.json({ success: true, message: 'Email sent successfully' });
  } catch (error) {
    console.error('Email sending error:', error);
    res.status(500).json({ error: 'Failed to send email' });
  }
});

// Error handling middleware
app.use((error, req, res, next) => {
  if (error instanceof multer.MulterError) {
    if (error.code === 'LIMIT_FILE_SIZE') {
      return res.status(400).json({ error: 'File too large' });
    }
  }
  
  console.error(error);
  res.status(500).json({ error: 'Internal server error' });
});

app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});
