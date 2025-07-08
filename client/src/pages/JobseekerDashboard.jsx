import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { doc, updateDoc, collection, query, where, getDocs } from 'firebase/firestore';
import { ref, uploadBytes, getDownloadURL } from 'firebase/storage';
import { db, storage } from '../config/firebase';
import { Upload, FileText, Briefcase, Star, Mail } from 'lucide-react';
import toast from 'react-hot-toast';

const JobseekerDashboard = () => {
  const { userProfile, fetchUserProfile } = useAuth();
  const [uploading, setUploading] = useState(false);
  const [applications, setApplications] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchApplications();
  }, []);

  const fetchApplications = async () => {
    try {
      const q = query(
        collection(db, 'applications'),
        where('applicantId', '==', userProfile?.uid)
      );
      const querySnapshot = await getDocs(q);
      const apps = [];
      querySnapshot.forEach((doc) => {
        apps.push({ id: doc.id, ...doc.data() });
      });
      setApplications(apps);
    } catch (error) {
      console.error('Error fetching applications:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleResumeUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    // Validate file type
    if (file.type !== 'application/pdf') {
      toast.error('Please upload a PDF file');
      return;
    }

    // Validate file size (5MB limit)
    if (file.size > 5 * 1024 * 1024) {
      toast.error('File size must be less than 5MB');
      return;
    }

    setUploading(true);

    try {
      // Upload file to Firebase Storage
      const storageRef = ref(storage, `resumes/${userProfile.uid}/${file.name}`);
      const snapshot = await uploadBytes(storageRef, file);
      const downloadURL = await getDownloadURL(snapshot.ref);

      // Parse resume content (simplified version)
      const extractedData = await parseResume(file);

      // Update user profile with resume URL and extracted data
      const userDocRef = doc(db, 'users', userProfile.uid);
      await updateDoc(userDocRef, {
        'profile.resumeUrl': downloadURL,
        'profile.skills': extractedData.skills,
        'profile.experience': extractedData.experience,
        'profile.education': extractedData.education,
        updatedAt: new Date().toISOString()
      });

      // Refresh user profile
      await fetchUserProfile(userProfile.uid);
      
      toast.success('Resume uploaded and parsed successfully!');
    } catch (error) {
      console.error('Error uploading resume:', error);
      toast.error('Failed to upload resume');
    } finally {
      setUploading(false);
    }
  };

  // Simplified resume parsing function
  const parseResume = async (file) => {
    // In a real application, you would use a proper resume parsing service
    // For now, we'll return some mock extracted data
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve({
          skills: ['JavaScript', 'React', 'Node.js', 'Python', 'SQL'],
          experience: '3 years of software development experience',
          education: 'Bachelor of Science in Computer Science'
        });
      }, 2000);
    });
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto space-y-8">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold text-gray-900">
          Welcome back, {userProfile?.username}!
        </h1>
        <div className="text-sm text-gray-600">
          Job Seeker Dashboard
        </div>
      </div>

      {/* Profile Summary */}
      <div className="grid md:grid-cols-2 gap-8">
        {/* Resume Upload Section */}
        <div className="card">
          <h2 className="text-xl font-semibold mb-4 flex items-center">
            <FileText className="mr-2" size={24} />
            Resume Management
          </h2>
          
          {userProfile?.profile?.resumeUrl ? (
            <div className="space-y-4">
              <div className="p-4 bg-green-50 border border-green-200 rounded-lg">
                <p className="text-green-800 font-medium">✓ Resume uploaded successfully</p>
                <a 
                  href={userProfile.profile.resumeUrl} 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="text-primary-600 hover:text-primary-700 text-sm"
                >
                  View Resume
                </a>
              </div>
              
              <div>
                <h3 className="font-medium mb-2">Extracted Skills:</h3>
                <div className="flex flex-wrap gap-2">
                  {userProfile.profile.skills?.map((skill, index) => (
                    <span 
                      key={index}
                      className="bg-primary-100 text-primary-800 px-2 py-1 rounded text-sm"
                    >
                      {skill}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          ) : (
            <div className="text-center py-8">
              <Upload className="mx-auto mb-4 text-gray-400" size={48} />
              <p className="text-gray-600 mb-4">Upload your resume to get started</p>
            </div>
          )}

          <div className="mt-4">
            <label className="block">
              <input
                type="file"
                accept=".pdf"
                onChange={handleResumeUpload}
                disabled={uploading}
                className="hidden"
              />
              <div className="btn-primary text-center cursor-pointer disabled:opacity-50">
                {uploading ? 'Processing Resume...' : 'Upload New Resume'}
              </div>
            </label>
            <p className="text-xs text-gray-500 mt-2">
              PDF files only, max 5MB
            </p>
          </div>
        </div>

        {/* Profile Information */}
        <div className="card">
          <h2 className="text-xl font-semibold mb-4">Profile Information</h2>
          <div className="space-y-3">
            <div>
              <label className="text-sm font-medium text-gray-600">Email</label>
              <p className="text-gray-900">{userProfile?.email}</p>
            </div>
            <div>
              <label className="text-sm font-medium text-gray-600">Experience</label>
              <p className="text-gray-900">
                {userProfile?.profile?.experience || 'Not specified'}
              </p>
            </div>
            <div>
              <label className="text-sm font-medium text-gray-600">Education</label>
              <p className="text-gray-900">
                {userProfile?.profile?.education || 'Not specified'}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Recent Applications */}
      <div className="card">
        <h2 className="text-xl font-semibold mb-4 flex items-center">
          <Briefcase className="mr-2" size={24} />
          Recent Applications
        </h2>
        
        {applications.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            <Briefcase className="mx-auto mb-4 text-gray-400" size={48} />
            <p>No applications yet. Start browsing jobs!</p>
          </div>
        ) : (
          <div className="space-y-4">
            {applications.slice(0, 5).map((application) => (
              <div key={application.id} className="border border-gray-200 rounded-lg p-4">
                <div className="flex justify-between items-start">
                  <div>
                    <h3 className="font-medium">{application.jobTitle}</h3>
                    <p className="text-sm text-gray-600">{application.companyName}</p>
                    <div className="flex items-center mt-2">
                      <Star className="text-yellow-500 mr-1" size={16} />
                      <span className="text-sm">
                        Compatibility: {application.compatibilityScore}%
                      </span>
                    </div>
                  </div>
                  <div className="text-right">
                    <span className={`px-2 py-1 rounded text-xs ${
                      application.status === 'pending' 
                        ? 'bg-yellow-100 text-yellow-800'
                        : application.status === 'accepted'
                        ? 'bg-green-100 text-green-800'
                        : 'bg-red-100 text-red-800'
                    }`}>
                      {application.status}
                    </span>
                    <p className="text-xs text-gray-500 mt-1">
                      {new Date(application.appliedAt).toLocaleDateString()}
                    </p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default JobseekerDashboard;
