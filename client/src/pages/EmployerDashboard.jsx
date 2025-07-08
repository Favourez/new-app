import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { collection, addDoc, query, where, getDocs, doc, updateDoc } from 'firebase/firestore';
import { db } from '../config/firebase';
import { Plus, Briefcase, Users, Eye, Star } from 'lucide-react';
import toast from 'react-hot-toast';

const EmployerDashboard = () => {
  const { userProfile } = useAuth();
  const [jobs, setJobs] = useState([]);
  const [applications, setApplications] = useState([]);
  const [showJobForm, setShowJobForm] = useState(false);
  const [loading, setLoading] = useState(true);
  const [jobForm, setJobForm] = useState({
    title: '',
    description: '',
    requirements: '',
    skills: '',
    salary: '',
    location: '',
    type: 'full-time'
  });

  useEffect(() => {
    fetchJobs();
    fetchApplications();
  }, []);

  const fetchJobs = async () => {
    try {
      const q = query(
        collection(db, 'jobs'),
        where('employerId', '==', userProfile?.uid)
      );
      const querySnapshot = await getDocs(q);
      const jobsList = [];
      querySnapshot.forEach((doc) => {
        jobsList.push({ id: doc.id, ...doc.data() });
      });
      setJobs(jobsList);
    } catch (error) {
      console.error('Error fetching jobs:', error);
    }
  };

  const fetchApplications = async () => {
    try {
      const q = query(
        collection(db, 'applications'),
        where('employerId', '==', userProfile?.uid)
      );
      const querySnapshot = await getDocs(q);
      const appsList = [];
      querySnapshot.forEach((doc) => {
        appsList.push({ id: doc.id, ...doc.data() });
      });
      setApplications(appsList);
    } catch (error) {
      console.error('Error fetching applications:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleJobSubmit = async (e) => {
    e.preventDefault();
    
    try {
      const skillsArray = jobForm.skills.split(',').map(skill => skill.trim()).filter(skill => skill);
      
      const jobData = {
        ...jobForm,
        skills: skillsArray,
        employerId: userProfile.uid,
        companyName: userProfile.profile?.companyName || userProfile.username,
        postedAt: new Date().toISOString(),
        status: 'active'
      };

      await addDoc(collection(db, 'jobs'), jobData);
      
      toast.success('Job posted successfully!');
      setShowJobForm(false);
      setJobForm({
        title: '',
        description: '',
        requirements: '',
        skills: '',
        salary: '',
        location: '',
        type: 'full-time'
      });
      
      fetchJobs();
    } catch (error) {
      console.error('Error posting job:', error);
      toast.error('Failed to post job');
    }
  };

  const handleApplicationStatus = async (applicationId, status) => {
    try {
      await updateDoc(doc(db, 'applications', applicationId), {
        status,
        updatedAt: new Date().toISOString()
      });
      
      toast.success(`Application ${status}`);
      fetchApplications();
    } catch (error) {
      console.error('Error updating application:', error);
      toast.error('Failed to update application');
    }
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
          Employer Dashboard
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid md:grid-cols-3 gap-6">
        <div className="card text-center">
          <Briefcase className="mx-auto mb-2 text-primary-600" size={32} />
          <h3 className="text-2xl font-bold text-gray-900">{jobs.length}</h3>
          <p className="text-gray-600">Active Jobs</p>
        </div>
        
        <div className="card text-center">
          <Users className="mx-auto mb-2 text-green-600" size={32} />
          <h3 className="text-2xl font-bold text-gray-900">{applications.length}</h3>
          <p className="text-gray-600">Total Applications</p>
        </div>
        
        <div className="card text-center">
          <Eye className="mx-auto mb-2 text-blue-600" size={32} />
          <h3 className="text-2xl font-bold text-gray-900">
            {applications.filter(app => app.status === 'pending').length}
          </h3>
          <p className="text-gray-600">Pending Reviews</p>
        </div>
      </div>

      {/* Job Management */}
      <div className="card">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-xl font-semibold">Job Management</h2>
          <button
            onClick={() => setShowJobForm(!showJobForm)}
            className="btn-primary flex items-center"
          >
            <Plus className="mr-2" size={20} />
            Post New Job
          </button>
        </div>

        {showJobForm && (
          <form onSubmit={handleJobSubmit} className="mb-8 p-6 bg-gray-50 rounded-lg space-y-4">
            <div className="grid md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Job Title
                </label>
                <input
                  type="text"
                  value={jobForm.title}
                  onChange={(e) => setJobForm({...jobForm, title: e.target.value})}
                  className="input-field"
                  required
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Location
                </label>
                <input
                  type="text"
                  value={jobForm.location}
                  onChange={(e) => setJobForm({...jobForm, location: e.target.value})}
                  className="input-field"
                  required
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Job Description
              </label>
              <textarea
                value={jobForm.description}
                onChange={(e) => setJobForm({...jobForm, description: e.target.value})}
                className="input-field h-32"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Requirements
              </label>
              <textarea
                value={jobForm.requirements}
                onChange={(e) => setJobForm({...jobForm, requirements: e.target.value})}
                className="input-field h-24"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Required Skills (comma-separated)
              </label>
              <input
                type="text"
                value={jobForm.skills}
                onChange={(e) => setJobForm({...jobForm, skills: e.target.value})}
                className="input-field"
                placeholder="JavaScript, React, Node.js"
                required
              />
            </div>

            <div className="grid md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Salary Range
                </label>
                <input
                  type="text"
                  value={jobForm.salary}
                  onChange={(e) => setJobForm({...jobForm, salary: e.target.value})}
                  className="input-field"
                  placeholder="$50,000 - $70,000"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Job Type
                </label>
                <select
                  value={jobForm.type}
                  onChange={(e) => setJobForm({...jobForm, type: e.target.value})}
                  className="input-field"
                >
                  <option value="full-time">Full Time</option>
                  <option value="part-time">Part Time</option>
                  <option value="contract">Contract</option>
                  <option value="internship">Internship</option>
                </select>
              </div>
            </div>

            <div className="flex space-x-4">
              <button type="submit" className="btn-primary">
                Post Job
              </button>
              <button 
                type="button" 
                onClick={() => setShowJobForm(false)}
                className="btn-secondary"
              >
                Cancel
              </button>
            </div>
          </form>
        )}

        {/* Jobs List */}
        <div className="space-y-4">
          {jobs.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              <Briefcase className="mx-auto mb-4 text-gray-400" size={48} />
              <p>No jobs posted yet. Create your first job posting!</p>
            </div>
          ) : (
            jobs.map((job) => (
              <div key={job.id} className="border border-gray-200 rounded-lg p-4">
                <div className="flex justify-between items-start">
                  <div>
                    <h3 className="font-medium text-lg">{job.title}</h3>
                    <p className="text-gray-600">{job.location} • {job.type}</p>
                    <div className="flex flex-wrap gap-2 mt-2">
                      {job.skills?.map((skill, index) => (
                        <span 
                          key={index}
                          className="bg-primary-100 text-primary-800 px-2 py-1 rounded text-xs"
                        >
                          {skill}
                        </span>
                      ))}
                    </div>
                  </div>
                  <div className="text-right">
                    <span className="text-sm text-gray-500">
                      {applications.filter(app => app.jobId === job.id).length} applications
                    </span>
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      </div>

      {/* Recent Applications */}
      <div className="card">
        <h2 className="text-xl font-semibold mb-4">Recent Applications</h2>
        
        {applications.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            <Users className="mx-auto mb-4 text-gray-400" size={48} />
            <p>No applications received yet.</p>
          </div>
        ) : (
          <div className="space-y-4">
            {applications.slice(0, 10).map((application) => (
              <div key={application.id} className="border border-gray-200 rounded-lg p-4">
                <div className="flex justify-between items-start">
                  <div>
                    <h3 className="font-medium">{application.applicantName}</h3>
                    <p className="text-sm text-gray-600">{application.jobTitle}</p>
                    <div className="flex items-center mt-2">
                      <Star className="text-yellow-500 mr-1" size={16} />
                      <span className="text-sm">
                        Compatibility: {application.compatibilityScore}%
                      </span>
                    </div>
                  </div>
                  <div className="flex items-center space-x-2">
                    {application.status === 'pending' && (
                      <>
                        <button
                          onClick={() => handleApplicationStatus(application.id, 'accepted')}
                          className="bg-green-600 text-white px-3 py-1 rounded text-sm hover:bg-green-700"
                        >
                          Accept
                        </button>
                        <button
                          onClick={() => handleApplicationStatus(application.id, 'rejected')}
                          className="bg-red-600 text-white px-3 py-1 rounded text-sm hover:bg-red-700"
                        >
                          Reject
                        </button>
                      </>
                    )}
                    <span className={`px-2 py-1 rounded text-xs ${
                      application.status === 'pending' 
                        ? 'bg-yellow-100 text-yellow-800'
                        : application.status === 'accepted'
                        ? 'bg-green-100 text-green-800'
                        : 'bg-red-100 text-red-800'
                    }`}>
                      {application.status}
                    </span>
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

export default EmployerDashboard;
