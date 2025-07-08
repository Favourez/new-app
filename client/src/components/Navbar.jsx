import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { LogOut, User, Briefcase, MessageCircle } from 'lucide-react';
import toast from 'react-hot-toast';

const Navbar = () => {
  const { currentUser, userProfile, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = async () => {
    try {
      await logout();
      toast.success('Logged out successfully');
      navigate('/');
    } catch (error) {
      toast.error('Failed to logout');
    }
  };

  return (
    <nav className="bg-white shadow-lg">
      <div className="container mx-auto px-4">
        <div className="flex justify-between items-center py-4">
          <Link to="/" className="text-2xl font-bold text-primary-600">
            JobPortal
          </Link>

          <div className="flex items-center space-x-4">
            {currentUser ? (
              <>
                <Link 
                  to="/dashboard" 
                  className="flex items-center space-x-1 text-gray-700 hover:text-primary-600"
                >
                  <User size={20} />
                  <span>Dashboard</span>
                </Link>
                
                <Link 
                  to="/jobs" 
                  className="flex items-center space-x-1 text-gray-700 hover:text-primary-600"
                >
                  <Briefcase size={20} />
                  <span>Jobs</span>
                </Link>
                
                <Link 
                  to="/chat" 
                  className="flex items-center space-x-1 text-gray-700 hover:text-primary-600"
                >
                  <MessageCircle size={20} />
                  <span>Chat</span>
                </Link>

                <div className="flex items-center space-x-2">
                  <span className="text-sm text-gray-600">
                    {userProfile?.username || currentUser.email}
                  </span>
                  <span className="text-xs bg-primary-100 text-primary-800 px-2 py-1 rounded">
                    {userProfile?.userType}
                  </span>
                </div>

                <button
                  onClick={handleLogout}
                  className="flex items-center space-x-1 text-gray-700 hover:text-red-600"
                >
                  <LogOut size={20} />
                  <span>Logout</span>
                </button>
              </>
            ) : (
              <>
                <Link 
                  to="/login" 
                  className="text-gray-700 hover:text-primary-600"
                >
                  Login
                </Link>
                <Link 
                  to="/register" 
                  className="btn-primary"
                >
                  Register
                </Link>
              </>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
