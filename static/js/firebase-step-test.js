// Step-by-step Firebase initialization test
console.log('Loading firebase-step-test.js...');

// Firebase configuration
const firebaseConfig = {
  apiKey: "AIzaSyBWsRNqwgqxsl7l4IWEjhuPcRt3LjUEl-g",
  authDomain: "news-feed-61652.firebaseapp.com",
  projectId: "news-feed-61652",
  storageBucket: "news-feed-61652.firebasestorage.app",
  messagingSenderId: "60774498266",
  appId: "1:60774498266:web:0642f93013b21c70944ae3",
  measurementId: "G-KT08QR87DH"
};

let stepTestResults = {
    cdnLoaded: false,
    appInitialized: false,
    firestoreConnected: false,
    testWriteSuccess: false,
    testReadSuccess: false,
    error: null
};

function logStep(message, success = null) {
    console.log(message);
    if (window.stepLog) {
        window.stepLog(message, success ? 'success' : success === false ? 'error' : 'info');
    }
}

function updateStepResults(step, success, error = null) {
    stepTestResults[step] = success;
    if (error) stepTestResults.error = error;
    
    if (window.updateStepStatus) {
        window.updateStepStatus(step, success, error);
    }
}

async function runStepByStepTest() {
    logStep('🚀 Starting step-by-step Firebase test...');
    
    try {
        // Step 1: Check CDN
        logStep('Step 1: Checking Firebase CDN...');
        if (typeof firebase === 'undefined') {
            throw new Error('Firebase CDN not loaded');
        }
        logStep('✅ Step 1: Firebase CDN loaded successfully', true);
        updateStepResults('cdnLoaded', true);
        
        // Step 2: Initialize Firebase App
        logStep('Step 2: Initializing Firebase app...');
        let app;
        try {
            // Check if already initialized
            if (firebase.apps.length > 0) {
                app = firebase.apps[0];
                logStep('ℹ️ Firebase app already initialized');
            } else {
                app = firebase.initializeApp(firebaseConfig);
                logStep('✅ Step 2: Firebase app initialized successfully', true);
            }
            updateStepResults('appInitialized', true);
        } catch (error) {
            logStep(`❌ Step 2 failed: ${error.message}`, false);
            updateStepResults('appInitialized', false, error.message);
            throw error;
        }
        
        // Step 3: Initialize Firestore
        logStep('Step 3: Connecting to Firestore...');
        let db;
        try {
            db = firebase.firestore();
            
            // Test Firestore settings
            db.settings({
                cacheSizeBytes: firebase.firestore.CACHE_SIZE_UNLIMITED
            });
            
            logStep('✅ Step 3: Firestore connected successfully', true);
            updateStepResults('firestoreConnected', true);
        } catch (error) {
            logStep(`❌ Step 3 failed: ${error.message}`, false);
            updateStepResults('firestoreConnected', false, error.message);
            throw error;
        }
        
        // Step 4: Test Write Operation
        logStep('Step 4: Testing write operation...');
        try {
            const testDoc = {
                test: true,
                message: 'Step-by-step test write',
                timestamp: firebase.firestore.FieldValue.serverTimestamp(),
                userAgent: navigator.userAgent,
                url: window.location.href
            };
            
            const docRef = await db.collection('step-test').add(testDoc);
            logStep(`✅ Step 4: Write test successful, document ID: ${docRef.id}`, true);
            updateStepResults('testWriteSuccess', true);
        } catch (error) {
            logStep(`❌ Step 4 failed: ${error.message}`, false);
            updateStepResults('testWriteSuccess', false, error.message);
            
            // Log more details about the error
            logStep(`Error code: ${error.code}`);
            logStep(`Error details: ${JSON.stringify(error)}`);
            throw error;
        }
        
        // Step 5: Test Read Operation
        logStep('Step 5: Testing read operation...');
        try {
            const querySnapshot = await db.collection('step-test').limit(3).get();
            logStep(`✅ Step 5: Read test successful, found ${querySnapshot.size} documents`, true);
            updateStepResults('testReadSuccess', true);
            
            // Log some document details
            querySnapshot.forEach((doc, index) => {
                logStep(`Document ${index + 1}: ${doc.id}`);
            });
        } catch (error) {
            logStep(`❌ Step 5 failed: ${error.message}`, false);
            updateStepResults('testReadSuccess', false, error.message);
            throw error;
        }
        
        // Success - Create working service
        logStep('🎉 All tests passed! Creating working Firebase service...');
        
        window.workingFirebaseService = {
            db: db,
            
            async createPost(postData) {
                try {
                    logStep('Creating post with working service...');
                    const docRef = await db.collection('posts').add({
                        ...postData,
                        createdAt: firebase.firestore.FieldValue.serverTimestamp(),
                        updatedAt: firebase.firestore.FieldValue.serverTimestamp(),
                        likesCount: 0,
                        commentsCount: 0,
                        sharesCount: 0,
                        likes: [],
                        isActive: true
                    });
                    logStep(`✅ Post created successfully: ${docRef.id}`);
                    return { success: true, id: docRef.id };
                } catch (error) {
                    logStep(`❌ Error creating post: ${error.message}`);
                    return { success: false, error: error.message };
                }
            },
            
            async getPosts(limitCount = 20) {
                try {
                    logStep('Getting posts with working service...');
                    const querySnapshot = await db.collection('posts')
                        .where('isActive', '==', true)
                        .orderBy('createdAt', 'desc')
                        .limit(limitCount)
                        .get();
                    
                    const posts = [];
                    querySnapshot.forEach((doc) => {
                        const data = doc.data();
                        // Convert Firestore timestamp to ISO string
                        if (data.createdAt && data.createdAt.toDate) {
                            data.createdAt = data.createdAt.toDate().toISOString();
                        }
                        if (data.updatedAt && data.updatedAt.toDate) {
                            data.updatedAt = data.updatedAt.toDate().toISOString();
                        }
                        posts.push({ id: doc.id, ...data });
                    });
                    
                    logStep(`✅ Retrieved ${posts.length} posts`);
                    return { success: true, data: posts };
                } catch (error) {
                    logStep(`❌ Error getting posts: ${error.message}`);
                    return { success: false, error: error.message };
                }
            },
            
            async toggleLike(postId, userId) {
                try {
                    const postRef = db.collection('posts').doc(postId);
                    const postDoc = await postRef.get();
                    
                    if (!postDoc.exists) {
                        return { success: false, error: 'Post not found' };
                    }
                    
                    const postData = postDoc.data();
                    const likes = postData.likes || [];
                    const isLiked = likes.includes(userId);
                    
                    if (isLiked) {
                        await postRef.update({
                            likes: firebase.firestore.FieldValue.arrayRemove(userId),
                            likesCount: firebase.firestore.FieldValue.increment(-1)
                        });
                        return { success: true, action: 'unliked' };
                    } else {
                        await postRef.update({
                            likes: firebase.firestore.FieldValue.arrayUnion(userId),
                            likesCount: firebase.firestore.FieldValue.increment(1)
                        });
                        return { success: true, action: 'liked' };
                    }
                } catch (error) {
                    return { success: false, error: error.message };
                }
            }
        };
        
        window.firebaseStepTestReady = true;
        logStep('🎉 Working Firebase service created and ready!');
        
    } catch (error) {
        logStep(`💥 Test failed at step: ${error.message}`, false);
        window.firebaseStepTestReady = false;
        
        // Provide troubleshooting suggestions
        if (error.message.includes('permission-denied')) {
            logStep('💡 Suggestion: Check Firebase security rules');
        } else if (error.message.includes('network')) {
            logStep('💡 Suggestion: Check internet connection and firewall');
        } else if (error.message.includes('api-key')) {
            logStep('💡 Suggestion: Verify Firebase API key and project configuration');
        }
    }
}

// Auto-start test when Firebase CDN is ready
function waitForFirebaseAndTest() {
    if (typeof firebase !== 'undefined') {
        logStep('Firebase CDN detected, starting test...');
        runStepByStepTest();
    } else {
        setTimeout(waitForFirebaseAndTest, 500);
    }
}

// Start the test
waitForFirebaseAndTest();

console.log('firebase-step-test.js loaded');
