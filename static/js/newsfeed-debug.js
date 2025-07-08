// Debug version of News Feed Firebase service
console.log('Loading newsfeed-debug.js...');

// Simple Firebase configuration test
const firebaseConfig = {
  apiKey: "AIzaSyBWsRNqwgqxsl7l4IWEjhuPcRt3LjUEl-g",
  authDomain: "news-feed-61652.firebaseapp.com",
  projectId: "news-feed-61652",
  storageBucket: "news-feed-61652.firebasestorage.app",
  messagingSenderId: "60774498266",
  appId: "1:60774498266:web:0642f93013b21c70944ae3",
  measurementId: "G-KT08QR87DH"
};

console.log('Firebase config:', firebaseConfig);

// Test if Firebase modules can be imported
async function testFirebaseImport() {
    try {
        console.log('Testing Firebase imports...');
        
        const { initializeApp } = await import("https://www.gstatic.com/firebasejs/11.8.1/firebase-app.js");
        console.log('✅ Firebase app imported successfully');
        
        const { getFirestore, collection, addDoc, getDocs, getDoc, doc, updateDoc, deleteDoc, query, where, orderBy, limit, increment, arrayUnion, arrayRemove, onSnapshot } = await import("https://www.gstatic.com/firebasejs/11.8.1/firebase-firestore.js");
        console.log('✅ Firestore imported successfully');
        
        const { getStorage, ref, uploadBytes, getDownloadURL } = await import("https://www.gstatic.com/firebasejs/11.8.1/firebase-storage.js");
        console.log('✅ Storage imported successfully');
        
        // Initialize Firebase
        console.log('Initializing Firebase...');
        const app = initializeApp(firebaseConfig, 'newsfeed-debug');
        console.log('✅ Firebase app initialized:', app);
        
        const db = getFirestore(app);
        console.log('✅ Firestore initialized:', db);
        
        const storage = getStorage(app);
        console.log('✅ Storage initialized:', storage);
        
        // Test basic Firestore operation
        console.log('Testing Firestore write...');
        const testData = {
            test: true,
            timestamp: new Date().toISOString(),
            message: 'Debug test from JobSync'
        };
        
        const docRef = await addDoc(collection(db, 'debug-test'), testData);
        console.log('✅ Test document written with ID:', docRef.id);
        
        // Test reading
        console.log('Testing Firestore read...');
        const querySnapshot = await getDocs(collection(db, 'debug-test'));
        console.log('✅ Read', querySnapshot.size, 'documents from debug-test collection');
        
        // Create simplified service
        window.debugNewsFeedService = {
            db: db,
            storage: storage,
            functions: {
                collection,
                addDoc,
                getDocs,
                getDoc,
                doc,
                updateDoc,
                deleteDoc,
                query,
                where,
                orderBy,
                limit,
                increment,
                arrayUnion,
                arrayRemove,
                onSnapshot
            },
            
            async createPost(postData) {
                try {
                    console.log('Debug: Creating post with data:', postData);
                    const docRef = await addDoc(collection(db, 'posts'), {
                        ...postData,
                        createdAt: new Date().toISOString(),
                        updatedAt: new Date().toISOString(),
                        likesCount: 0,
                        commentsCount: 0,
                        sharesCount: 0,
                        likes: [],
                        isActive: true
                    });
                    console.log('Debug: Post created with ID:', docRef.id);
                    return { success: true, id: docRef.id };
                } catch (error) {
                    console.error('Debug: Error creating post:', error);
                    return { success: false, error: error.message };
                }
            },
            
            async getPosts(limitCount = 20) {
                try {
                    console.log('Debug: Getting posts...');
                    const q = query(
                        collection(db, 'posts'),
                        where('isActive', '==', true),
                        orderBy('createdAt', 'desc'),
                        limit(limitCount)
                    );
                    
                    const querySnapshot = await getDocs(q);
                    const posts = [];
                    querySnapshot.forEach((doc) => {
                        posts.push({ id: doc.id, ...doc.data() });
                    });
                    console.log('Debug: Retrieved', posts.length, 'posts');
                    return { success: true, data: posts };
                } catch (error) {
                    console.error('Debug: Error getting posts:', error);
                    return { success: false, error: error.message };
                }
            }
        };
        
        console.log('✅ Debug news feed service created');
        return true;
        
    } catch (error) {
        console.error('❌ Firebase import/initialization failed:', error);
        return false;
    }
}

// Auto-initialize
testFirebaseImport().then(success => {
    if (success) {
        console.log('🎉 Firebase debug service ready!');
        window.firebaseDebugReady = true;
    } else {
        console.error('💥 Firebase debug service failed to initialize');
        window.firebaseDebugReady = false;
    }
});

console.log('newsfeed-debug.js loaded');
