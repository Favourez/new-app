import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { collection, getDocs, addDoc, query, where } from 'firebase/firestore';
import { db } from '../config/firebase';
import { Search, MapPin, Clock, DollarSign, Star, Send } from 'lucide-react';
import toast from 'react-hot-toast';
import emailjs from '@emailjs/browser';

const Jobs = () => {
  const { userProfile } = useAuth();
  const [jobs, setJobs] = useState([]);
  const [filteredJobs, setFilteredJobs] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [locationFilter, setLocationFilter] = useState('');
  const [loading, setLoading] = useState(true);
  const [applying, setApplying] = useState(null);

  useEffect(() => {
    fetchJobs();
  }, []);

  useEffect(() => {
    filterJobs();
  }, [jobs, searchTerm, locationFilter]);

  const fetchJobs = async () => {
    try {
      const querySnapshot = await getDocs(collection(db, 'jobs'));
      const jobsList = [];
      querySnapshot.forEach((doc) => {
        const jobData = { id: doc.id, ...doc.data() };
        // Don't show jobs posted by the current user (if they're an employer)
        if (jobData.employerId !== userProfile?.uid) {
          jobsList.push(jobData);
        }
      });
      setJobs(jobsList);
    } catch (error) {
      console.error('Error fetching jobs:', error);
      toast.error('Failed to load jobs');
    } finally {
      setLoading(false);
    }
  };

  const filterJobs = () => {
    let filtered = jobs;

    if (searchTerm) {
      filtered = filtered.filter(job =>
        job.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
        job.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
        job.skills?.some(skill => skill.toLowerCase().includes(searchTerm.toLowerCase()))
      );
    }

    if (locationFilter) {
      filtered = filtered.filter(job =>
        job.location.toLowerCase().includes(locationFilter.toLowerCase())
      );
    }

    setFilteredJobs(filtered);
  };

  const calculateCompatibilityScore = (jobSkills, userSkills) => {
    if (!jobSkills || !userSkills || jobSkills.length === 0 || userSkills.length === 0) {
      return 0;
    }

    const matchingSkills = jobSkills.filter(jobSkill =>
      userSkills.some(userSkill =>
        userSkill.toLowerCase().includes(jobSkill.toLowerCase()) ||
        jobSkill.toLowerCase().includes(userSkill.toLowerCase())
      )
    );

    return Math.round((matchingSkills.length / jobSkills.length) * 100);
  };

  const handleApply = async (job) => {
    if (userProfile?.userType !== 'jobseeker') {
      toast.error('Only job seekers can apply for jobs');
      return;
    }

    if (!userProfile?.profile?.resumeUrl) {
      toast.error('Please upload your resume first');
      return;
    }

    setApplying(job.id);

    try {
      // Check if already applied
      const existingApplications = query(
        collection(db, 'applications'),
        where('jobId', '==', job.id),
        where('applicantId', '==', userProfile.uid)
      );
      const existingSnapshot = await getDocs(existingApplications);

      if (!existingSnapshot.empty) {
        toast.error('You have already applied for this job');
        setApplying(null);
        return;
      }

      const compatibilityScore = calculateCompatibilityScore(
        job.skills,
        userProfile.profile.skills
      );

      // Create application
      const applicationData = {
        jobId: job.id,
        jobTitle: job.title,
        employerId: job.employerId,
        companyName: job.companyName,
        applicantId: userProfile.uid,
        applicantName: userProfile.username,
        applicantEmail: userProfile.email,
        compatibilityScore,
        status: 'pending',
        appliedAt: new Date().toISOString(),
        resumeUrl: userProfile.profile.resumeUrl
      };

      await addDoc(collection(db, 'applications'), applicationData);

      // Send email notification
      await sendApplicationEmail(job, userProfile, compatibilityScore);

      toast.success('Application submitted successfully!');
    } catch (error) {
      console.error('Error applying for job:', error);
      toast.error('Failed to submit application');
    } finally {
      setApplying(null);
    }
  };

  const sendApplicationEmail = async (job, applicant, compatibilityScore) => {
    try {
      // Initialize EmailJS (you'll need to set up your EmailJS account)
      const templateParams = {
        to_email: applicant.email,
        applicant_name: applicant.username,
        job_title: job.title,
        company_name: job.companyName,
        compatibility_score: compatibilityScore,
        application_date: new Date().toLocaleDateString()
      };

      // Note: You'll need to configure EmailJS with your service ID, template ID, and public key
      // await emailjs.send('YOUR_SERVICE_ID', 'YOUR_TEMPLATE_ID', templateParams, 'YOUR_PUBLIC_KEY');
      
      console.log('Email would be sent with params:', templateParams);
    } catch (error) {
      console.error('Error sending email:', error);
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
      <div className="text-center">
        <h1 className="text-3xl font-bold text-gray-900 mb-4">Find Your Next Opportunity</h1>
        <p className="text-gray-600">Discover jobs that match your skills and experience</p>
      </div>

      {/* Search and Filters */}
      <div className="card">
        <div className="grid md:grid-cols-3 gap-4">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
            <input
              type="text"
              placeholder="Search jobs, skills, or keywords..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="input-field pl-10"
            />
          </div>
          
          <div className="relative">
            <MapPin className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
            <input
              type="text"
              placeholder="Location"
              value={locationFilter}
              onChange={(e) => setLocationFilter(e.target.value)}
              className="input-field pl-10"
            />
          </div>
          
          <div className="flex items-center justify-center">
            <span className="text-sm text-gray-600">
              {filteredJobs.length} jobs found
            </span>
          </div>
        </div>
      </div>

      {/* Jobs List */}
      <div className="space-y-6">
        {filteredJobs.length === 0 ? (
          <div className="text-center py-12">
            <Search className="mx-auto mb-4 text-gray-400" size={48} />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No jobs found</h3>
            <p className="text-gray-600">Try adjusting your search criteria</p>
          </div>
        ) : (
          filteredJobs.map((job) => {
            const compatibilityScore = calculateCompatibilityScore(
              job.skills,
              userProfile?.profile?.skills
            );

            return (
              <div key={job.id} className="card hover:shadow-lg transition-shadow">
                <div className="flex justify-between items-start mb-4">
                  <div>
                    <h2 className="text-xl font-semibold text-gray-900 mb-2">{job.title}</h2>
                    <p className="text-gray-600 mb-2">{job.companyName}</p>
                    
                    <div className="flex items-center space-x-4 text-sm text-gray-500 mb-3">
                      <div className="flex items-center">
                        <MapPin size={16} className="mr-1" />
                        {job.location}
                      </div>
                      <div className="flex items-center">
                        <Clock size={16} className="mr-1" />
                        {job.type}
                      </div>
                      {job.salary && (
                        <div className="flex items-center">
                          <DollarSign size={16} className="mr-1" />
                          {job.salary}
                        </div>
                      )}
                    </div>

                    {userProfile?.userType === 'jobseeker' && userProfile?.profile?.skills && (
                      <div className="flex items-center mb-3">
                        <Star className="text-yellow-500 mr-1" size={16} />
                        <span className="text-sm font-medium">
                          {compatibilityScore}% match
                        </span>
                      </div>
                    )}
                  </div>

                  {userProfile?.userType === 'jobseeker' && (
                    <button
                      onClick={() => handleApply(job)}
                      disabled={applying === job.id}
                      className="btn-primary flex items-center disabled:opacity-50"
                    >
                      <Send size={16} className="mr-2" />
                      {applying === job.id ? 'Applying...' : 'Apply Now'}
                    </button>
                  )}
                </div>

                <div className="mb-4">
                  <p className="text-gray-700 mb-3">{job.description}</p>
                  
                  <div className="mb-3">
                    <h4 className="font-medium text-gray-900 mb-2">Requirements:</h4>
                    <p className="text-gray-700 text-sm">{job.requirements}</p>
                  </div>

                  {job.skills && job.skills.length > 0 && (
                    <div>
                      <h4 className="font-medium text-gray-900 mb-2">Required Skills:</h4>
                      <div className="flex flex-wrap gap-2">
                        {job.skills.map((skill, index) => {
                          const isMatched = userProfile?.profile?.skills?.some(userSkill =>
                            userSkill.toLowerCase().includes(skill.toLowerCase()) ||
                            skill.toLowerCase().includes(userSkill.toLowerCase())
                          );

                          return (
                            <span
                              key={index}
                              className={`px-3 py-1 rounded-full text-sm ${
                                isMatched
                                  ? 'bg-green-100 text-green-800 border border-green-200'
                                  : 'bg-gray-100 text-gray-800'
                              }`}
                            >
                              {skill}
                              {isMatched && ' ✓'}
                            </span>
                          );
                        })}
                      </div>
                    </div>
                  )}
                </div>

                <div className="text-xs text-gray-500">
                  Posted on {new Date(job.postedAt).toLocaleDateString()}
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
};

export default Jobs;
