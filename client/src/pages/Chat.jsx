import React, { useState, useEffect, useRef } from 'react';
import { useAuth } from '../context/AuthContext';
import { ref, push, onValue, off } from 'firebase/database';
import { realtimeDb } from '../config/firebase';
import { Send, Users } from 'lucide-react';
import toast from 'react-hot-toast';

const Chat = () => {
  const { userProfile } = useAuth();
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  const [onlineUsers, setOnlineUsers] = useState([]);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    // Listen for messages
    const messagesRef = ref(realtimeDb, 'messages');
    const unsubscribeMessages = onValue(messagesRef, (snapshot) => {
      const data = snapshot.val();
      if (data) {
        const messagesList = Object.keys(data).map(key => ({
          id: key,
          ...data[key]
        })).sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp));
        setMessages(messagesList);
      }
    });

    // Listen for online users
    const onlineUsersRef = ref(realtimeDb, 'onlineUsers');
    const unsubscribeUsers = onValue(onlineUsersRef, (snapshot) => {
      const data = snapshot.val();
      if (data) {
        const usersList = Object.keys(data).map(key => ({
          id: key,
          ...data[key]
        }));
        setOnlineUsers(usersList);
      }
    });

    // Set user as online
    if (userProfile) {
      const userOnlineRef = ref(realtimeDb, `onlineUsers/${userProfile.uid}`);
      push(userOnlineRef, {
        username: userProfile.username,
        userType: userProfile.userType,
        lastSeen: new Date().toISOString()
      });
    }

    return () => {
      off(messagesRef, 'value', unsubscribeMessages);
      off(onlineUsersRef, 'value', unsubscribeUsers);
    };
  }, [userProfile]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleSendMessage = async (e) => {
    e.preventDefault();
    
    if (!newMessage.trim()) return;

    try {
      const messagesRef = ref(realtimeDb, 'messages');
      await push(messagesRef, {
        text: newMessage.trim(),
        userId: userProfile.uid,
        username: userProfile.username,
        userType: userProfile.userType,
        timestamp: new Date().toISOString()
      });

      setNewMessage('');
    } catch (error) {
      console.error('Error sending message:', error);
      toast.error('Failed to send message');
    }
  };

  const formatTime = (timestamp) => {
    return new Date(timestamp).toLocaleTimeString([], { 
      hour: '2-digit', 
      minute: '2-digit' 
    });
  };

  const formatDate = (timestamp) => {
    const date = new Date(timestamp);
    const today = new Date();
    const yesterday = new Date(today);
    yesterday.setDate(yesterday.getDate() - 1);

    if (date.toDateString() === today.toDateString()) {
      return 'Today';
    } else if (date.toDateString() === yesterday.toDateString()) {
      return 'Yesterday';
    } else {
      return date.toLocaleDateString();
    }
  };

  const groupMessagesByDate = (messages) => {
    const groups = {};
    messages.forEach(message => {
      const date = formatDate(message.timestamp);
      if (!groups[date]) {
        groups[date] = [];
      }
      groups[date].push(message);
    });
    return groups;
  };

  const messageGroups = groupMessagesByDate(messages);

  return (
    <div className="max-w-6xl mx-auto">
      <div className="grid lg:grid-cols-4 gap-6 h-[600px]">
        {/* Online Users Sidebar */}
        <div className="lg:col-span-1">
          <div className="card h-full">
            <h2 className="text-lg font-semibold mb-4 flex items-center">
              <Users className="mr-2" size={20} />
              Online Users ({onlineUsers.length})
            </h2>
            
            <div className="space-y-2 overflow-y-auto">
              {onlineUsers.map((user) => (
                <div key={user.id} className="flex items-center space-x-3 p-2 rounded-lg hover:bg-gray-50">
                  <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                  <div>
                    <p className="text-sm font-medium">{user.username}</p>
                    <p className="text-xs text-gray-500 capitalize">{user.userType}</p>
                  </div>
                </div>
              ))}
              
              {onlineUsers.length === 0 && (
                <p className="text-gray-500 text-sm">No users online</p>
              )}
            </div>
          </div>
        </div>

        {/* Chat Area */}
        <div className="lg:col-span-3">
          <div className="card h-full flex flex-col">
            <div className="border-b border-gray-200 pb-4 mb-4">
              <h1 className="text-xl font-semibold">Super Chat</h1>
              <p className="text-gray-600 text-sm">Connect with jobseekers and employers</p>
            </div>

            {/* Messages */}
            <div className="flex-1 overflow-y-auto space-y-4 mb-4">
              {Object.keys(messageGroups).length === 0 ? (
                <div className="text-center py-8 text-gray-500">
                  <p>No messages yet. Start the conversation!</p>
                </div>
              ) : (
                Object.keys(messageGroups).map(date => (
                  <div key={date}>
                    <div className="text-center my-4">
                      <span className="bg-gray-100 text-gray-600 px-3 py-1 rounded-full text-xs">
                        {date}
                      </span>
                    </div>
                    
                    {messageGroups[date].map((message) => (
                      <div
                        key={message.id}
                        className={`flex ${
                          message.userId === userProfile?.uid ? 'justify-end' : 'justify-start'
                        }`}
                      >
                        <div
                          className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                            message.userId === userProfile?.uid
                              ? 'bg-primary-600 text-white'
                              : 'bg-gray-100 text-gray-900'
                          }`}
                        >
                          {message.userId !== userProfile?.uid && (
                            <div className="flex items-center space-x-2 mb-1">
                              <span className="text-xs font-medium">
                                {message.username}
                              </span>
                              <span className={`text-xs px-1 rounded ${
                                message.userType === 'jobseeker' 
                                  ? 'bg-blue-100 text-blue-800' 
                                  : 'bg-green-100 text-green-800'
                              }`}>
                                {message.userType}
                              </span>
                            </div>
                          )}
                          
                          <p className="text-sm">{message.text}</p>
                          
                          <p className={`text-xs mt-1 ${
                            message.userId === userProfile?.uid 
                              ? 'text-primary-100' 
                              : 'text-gray-500'
                          }`}>
                            {formatTime(message.timestamp)}
                          </p>
                        </div>
                      </div>
                    ))}
                  </div>
                ))
              )}
              <div ref={messagesEndRef} />
            </div>

            {/* Message Input */}
            <form onSubmit={handleSendMessage} className="flex space-x-2">
              <input
                type="text"
                value={newMessage}
                onChange={(e) => setNewMessage(e.target.value)}
                placeholder="Type your message..."
                className="flex-1 input-field"
                maxLength={500}
              />
              <button
                type="submit"
                disabled={!newMessage.trim()}
                className="btn-primary flex items-center disabled:opacity-50"
              >
                <Send size={20} />
              </button>
            </form>
            
            <p className="text-xs text-gray-500 mt-2">
              Press Enter to send • {newMessage.length}/500 characters
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Chat;
