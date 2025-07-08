import React from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Users, Briefcase, MessageCircle, TrendingUp } from 'lucide-react';

const Home = () => {
  const { currentUser } = useAuth();

  return (
    <div className="max-w-6xl mx-auto">
      {/* Hero Section */}
      <div className="text-center py-20">
        <h1 className="text-5xl font-bold text-gray-900 mb-6">
          Find Your Dream Job or Perfect Candidate
        </h1>
        <p className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto">
          Connect jobseekers with employers through our intelligent matching system. 
          Upload your resume, get compatibility scores, and chat with potential matches.
        </p>
        
        {!currentUser && (
          <div className="space-x-4">
            <Link to="/register" className="btn-primary text-lg px-8 py-3">
              Get Started
            </Link>
            <Link to="/login" className="btn-secondary text-lg px-8 py-3">
              Sign In
            </Link>
          </div>
        )}
      </div>

      {/* Features Section */}
      <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8 py-16">
        <div className="text-center">
          <div className="bg-primary-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
            <Users className="text-primary-600" size={32} />
          </div>
          <h3 className="text-xl font-semibold mb-2">Dual User Types</h3>
          <p className="text-gray-600">
            Separate dashboards for jobseekers and employers with tailored features
          </p>
        </div>

        <div className="text-center">
          <div className="bg-primary-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
            <Briefcase className="text-primary-600" size={32} />
          </div>
          <h3 className="text-xl font-semibold mb-2">Smart Resume Parsing</h3>
          <p className="text-gray-600">
            AI-powered resume analysis extracts skills and experience automatically
          </p>
        </div>

        <div className="text-center">
          <div className="bg-primary-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
            <TrendingUp className="text-primary-600" size={32} />
          </div>
          <h3 className="text-xl font-semibold mb-2">Compatibility Scoring</h3>
          <p className="text-gray-600">
            Get matched with jobs based on your skills and experience level
          </p>
        </div>

        <div className="text-center">
          <div className="bg-primary-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
            <MessageCircle className="text-primary-600" size={32} />
          </div>
          <h3 className="text-xl font-semibold mb-2">Real-time Chat</h3>
          <p className="text-gray-600">
            Connect and communicate with other users through our integrated chat system
          </p>
        </div>
      </div>

      {/* How it Works */}
      <div className="py-16 bg-white rounded-lg shadow-sm">
        <h2 className="text-3xl font-bold text-center mb-12">How It Works</h2>
        
        <div className="grid md:grid-cols-2 gap-12">
          {/* For Jobseekers */}
          <div>
            <h3 className="text-2xl font-semibold mb-6 text-primary-600">For Jobseekers</h3>
            <div className="space-y-4">
              <div className="flex items-start space-x-3">
                <div className="bg-primary-600 text-white rounded-full w-6 h-6 flex items-center justify-center text-sm font-bold">1</div>
                <p>Create your account and complete your profile</p>
              </div>
              <div className="flex items-start space-x-3">
                <div className="bg-primary-600 text-white rounded-full w-6 h-6 flex items-center justify-center text-sm font-bold">2</div>
                <p>Upload your resume for automatic skill extraction</p>
              </div>
              <div className="flex items-start space-x-3">
                <div className="bg-primary-600 text-white rounded-full w-6 h-6 flex items-center justify-center text-sm font-bold">3</div>
                <p>Browse jobs and get compatibility scores</p>
              </div>
              <div className="flex items-start space-x-3">
                <div className="bg-primary-600 text-white rounded-full w-6 h-6 flex items-center justify-center text-sm font-bold">4</div>
                <p>Apply to jobs and receive email confirmations</p>
              </div>
            </div>
          </div>

          {/* For Employers */}
          <div>
            <h3 className="text-2xl font-semibold mb-6 text-primary-600">For Employers</h3>
            <div className="space-y-4">
              <div className="flex items-start space-x-3">
                <div className="bg-primary-600 text-white rounded-full w-6 h-6 flex items-center justify-center text-sm font-bold">1</div>
                <p>Register your company and set up your profile</p>
              </div>
              <div className="flex items-start space-x-3">
                <div className="bg-primary-600 text-white rounded-full w-6 h-6 flex items-center justify-center text-sm font-bold">2</div>
                <p>Post job listings with required skills</p>
              </div>
              <div className="flex items-start space-x-3">
                <div className="bg-primary-600 text-white rounded-full w-6 h-6 flex items-center justify-center text-sm font-bold">3</div>
                <p>Review applications with compatibility scores</p>
              </div>
              <div className="flex items-start space-x-3">
                <div className="bg-primary-600 text-white rounded-full w-6 h-6 flex items-center justify-center text-sm font-bold">4</div>
                <p>Connect with candidates through chat</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Home;
