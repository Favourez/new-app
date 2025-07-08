// Basic Firebase test using CDN imports
console.log('Loading firebase-basic-test.js...');

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

console.log('Firebase config loaded:', firebaseConfig);

// Function to test Firebase using CDN
function testFirebaseWithCDN() {
    console.log('Testing Firebase with CDN approach...');
    
    // Check if Firebase is available globally
    if (typeof firebase !== 'undefined') {
        console.log('✅ Firebase SDK found via CDN');
        
        try {
            // Initialize Firebase
            if (!firebase.apps.length) {
                firebase.initializeApp(firebaseConfig);
                console.log('✅ Firebase app initialized');
            }
            
            // Get Firestore
            const db = firebase.firestore();
            console.log('✅ Firestore initialized');
            
            // Test write operation
            console.log('Testing Firestore write...');
            db.collection('test-posts').add({
                content: 'Test post from CDN Firebase',
                authorId: 'test-user',
                authorName: 'Test User',
                createdAt: firebase.firestore.FieldValue.serverTimestamp(),
                test: true
            }).then((docRef) => {
                console.log('✅ Test document written with ID:', docRef.id);
                
                // Test read operation
                console.log('Testing Firestore read...');
                return db.collection('test-posts').limit(5).get();
            }).then((querySnapshot) => {
                console.log('✅ Read', querySnapshot.size, 'documents');
                querySnapshot.forEach((doc) => {
                    console.log('Document:', doc.id, doc.data());
                });
                
                // Create basic service
                window.basicFirebaseService = {
                    db: db,
                    
                    async createPost(postData) {
                        try {
                            console.log('Creating post with basic service:', postData);
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
                            console.log('✅ Post created with ID:', docRef.id);
                            return { success: true, id: docRef.id };
                        } catch (error) {
                            console.error('❌ Error creating post:', error);
                            return { success: false, error: error.message };
                        }
                    },
                    
                    async getPosts(limitCount = 20) {
                        try {
                            console.log('Getting posts with basic service...');
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
                            
                            console.log('✅ Retrieved', posts.length, 'posts');
                            return { success: true, data: posts };
                        } catch (error) {
                            console.error('❌ Error getting posts:', error);
                            return { success: false, error: error.message };
                        }
                    }
                };
                
                console.log('🎉 Basic Firebase service created and ready!');
                window.firebaseBasicReady = true;
                
            }).catch((error) => {
                console.error('❌ Firebase test failed:', error);
                window.firebaseBasicReady = false;
            });
            
        } catch (error) {
            console.error('❌ Firebase initialization failed:', error);
            window.firebaseBasicReady = false;
        }
        
    } else {
        console.error('❌ Firebase SDK not found. CDN may not be loaded.');
        window.firebaseBasicReady = false;
    }
}

// Wait for Firebase CDN to load
let cdnCheckCount = 0;
const cdnCheckInterval = setInterval(() => {
    cdnCheckCount++;
    
    if (typeof firebase !== 'undefined') {
        clearInterval(cdnCheckInterval);
        console.log('✅ Firebase CDN loaded, starting test...');
        testFirebaseWithCDN();
    } else if (cdnCheckCount > 20) {
        clearInterval(cdnCheckInterval);
        console.error('❌ Timeout waiting for Firebase CDN');
        window.firebaseBasicReady = false;
    } else {
        console.log(`⏳ Waiting for Firebase CDN... (${cdnCheckCount}/20)`);
    }
}, 500);

console.log('firebase-basic-test.js loaded, waiting for Firebase CDN...');
