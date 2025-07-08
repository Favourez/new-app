// News Feed Firebase configuration
import { initializeApp } from "https://www.gstatic.com/firebasejs/11.8.1/firebase-app.js";
import { getFirestore, collection, addDoc, getDocs, getDoc, doc, updateDoc, deleteDoc, query, where, orderBy, limit, increment, arrayUnion, arrayRemove, onSnapshot } from "https://www.gstatic.com/firebasejs/11.8.1/firebase-firestore.js";
import { getStorage, ref, uploadBytes, getDownloadURL } from "https://www.gstatic.com/firebasejs/11.8.1/firebase-storage.js";

const firebaseConfig = {
  apiKey: "AIzaSyBWsRNqwgqxsl7l4IWEjhuPcRt3LjUEl-g",
  authDomain: "news-feed-61652.firebaseapp.com",
  projectId: "news-feed-61652",
  storageBucket: "news-feed-61652.firebasestorage.app",
  messagingSenderId: "60774498266",
  appId: "1:60774498266:web:0642f93013b21c70944ae3",
  measurementId: "G-KT08QR87DH"
};

// Initialize Firebase for news feed
const newsFeedApp = initializeApp(firebaseConfig, 'newsfeed');
const newsFeedDB = getFirestore(newsFeedApp);
const newsFeedStorage = getStorage(newsFeedApp);

// News Feed Service Class
class NewsFeedService {
    constructor() {
        this.db = newsFeedDB;
        this.storage = newsFeedStorage;
        this.functions = {
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
        };
        this.storageFunctions = {
            ref,
            uploadBytes,
            getDownloadURL
        };
    }

    // Create a new post
    async createPost(postData) {
        try {
            const docRef = await this.functions.addDoc(
                this.functions.collection(this.db, 'posts'),
                {
                    ...postData,
                    createdAt: new Date().toISOString(),
                    updatedAt: new Date().toISOString(),
                    likesCount: 0,
                    commentsCount: 0,
                    sharesCount: 0,
                    likes: [],
                    isActive: true
                }
            );
            return { success: true, id: docRef.id };
        } catch (error) {
            console.error('Error creating post:', error);
            return { success: false, error: error.message };
        }
    }

    // Upload media (images/videos)
    async uploadMedia(file, postId) {
        try {
            const timestamp = Date.now();
            const fileName = `${postId}_${timestamp}_${file.name}`;
            const storageRef = this.storageFunctions.ref(this.storage, `posts/${fileName}`);

            const snapshot = await this.storageFunctions.uploadBytes(storageRef, file);
            const downloadURL = await this.storageFunctions.getDownloadURL(snapshot.ref);

            return { success: true, url: downloadURL, fileName: fileName };
        } catch (error) {
            console.error('Error uploading media:', error);
            return { success: false, error: error.message };
        }
    }

    // Get all posts with pagination
    async getPosts(limitCount = 20) {
        try {
            const q = this.functions.query(
                this.functions.collection(this.db, 'posts'),
                this.functions.where('isActive', '==', true),
                this.functions.orderBy('createdAt', 'desc'),
                this.functions.limit(limitCount)
            );

            const querySnapshot = await this.functions.getDocs(q);
            const posts = [];
            querySnapshot.forEach((doc) => {
                posts.push({ id: doc.id, ...doc.data() });
            });
            return { success: true, data: posts };
        } catch (error) {
            console.error('Error getting posts:', error);
            return { success: false, error: error.message };
        }
    }

    // Get posts by user
    async getPostsByUser(userId) {
        try {
            const q = this.functions.query(
                this.functions.collection(this.db, 'posts'),
                this.functions.where('authorId', '==', userId),
                this.functions.where('isActive', '==', true),
                this.functions.orderBy('createdAt', 'desc')
            );

            const querySnapshot = await this.functions.getDocs(q);
            const posts = [];
            querySnapshot.forEach((doc) => {
                posts.push({ id: doc.id, ...doc.data() });
            });
            return { success: true, data: posts };
        } catch (error) {
            console.error('Error getting user posts:', error);
            return { success: false, error: error.message };
        }
    }

    // Update post
    async updatePost(postId, updateData) {
        try {
            const postRef = this.functions.doc(this.db, 'posts', postId);
            await this.functions.updateDoc(postRef, {
                ...updateData,
                updatedAt: new Date().toISOString()
            });
            return { success: true };
        } catch (error) {
            console.error('Error updating post:', error);
            return { success: false, error: error.message };
        }
    }

    // Like/Unlike a post
    async toggleLike(postId, userId) {
        try {
            const postRef = this.functions.doc(this.db, 'posts', postId);
            const postDoc = await this.functions.getDoc(postRef);

            if (!postDoc.exists()) {
                return { success: false, error: 'Post not found' };
            }

            const postData = postDoc.data();
            const likes = postData.likes || [];
            const isLiked = likes.includes(userId);

            if (isLiked) {
                // Unlike
                await this.functions.updateDoc(postRef, {
                    likes: this.functions.arrayRemove(userId),
                    likesCount: this.functions.increment(-1),
                    updatedAt: new Date().toISOString()
                });
                return { success: true, action: 'unliked' };
            } else {
                // Like
                await this.functions.updateDoc(postRef, {
                    likes: this.functions.arrayUnion(userId),
                    likesCount: this.functions.increment(1),
                    updatedAt: new Date().toISOString()
                });
                return { success: true, action: 'liked' };
            }
        } catch (error) {
            console.error('Error toggling like:', error);
            return { success: false, error: error.message };
        }
    }

    // Get a single post
    async getPost(postId) {
        try {
            const postRef = this.functions.doc(this.db, 'posts', postId);
            const postDoc = await this.functions.getDoc(postRef);

            if (postDoc.exists()) {
                return { success: true, data: { id: postDoc.id, ...postDoc.data() } };
            } else {
                return { success: false, error: 'Post not found' };
            }
        } catch (error) {
            console.error('Error getting post:', error);
            return { success: false, error: error.message };
        }
    }

    // Add comment to post
    async addComment(postId, commentData) {
        try {
            // Add comment to comments collection
            const commentRef = await this.functions.addDoc(
                this.functions.collection(this.db, 'comments'),
                {
                    ...commentData,
                    postId: postId,
                    createdAt: new Date().toISOString(),
                    isActive: true
                }
            );

            // Update post comments count
            const postRef = this.functions.doc(this.db, 'posts', postId);
            await this.functions.updateDoc(postRef, {
                commentsCount: this.functions.increment(1),
                updatedAt: new Date().toISOString()
            });

            return { success: true, id: commentRef.id };
        } catch (error) {
            console.error('Error adding comment:', error);
            return { success: false, error: error.message };
        }
    }

    // Get comments for a post
    async getComments(postId) {
        try {
            const q = this.functions.query(
                this.functions.collection(this.db, 'comments'),
                this.functions.where('postId', '==', postId),
                this.functions.where('isActive', '==', true),
                this.functions.orderBy('createdAt', 'asc')
            );

            const querySnapshot = await this.functions.getDocs(q);
            const comments = [];
            querySnapshot.forEach((doc) => {
                comments.push({ id: doc.id, ...doc.data() });
            });
            return { success: true, data: comments };
        } catch (error) {
            console.error('Error getting comments:', error);
            return { success: false, error: error.message };
        }
    }

    // Share/Reshare a post
    async sharePost(originalPostId, userId, shareText = '') {
        try {
            // Create a new share post
            const shareData = {
                authorId: userId,
                type: 'share',
                originalPostId: originalPostId,
                content: shareText,
                isActive: true
            };

            const shareRef = await this.functions.addDoc(
                this.functions.collection(this.db, 'posts'),
                {
                    ...shareData,
                    createdAt: new Date().toISOString(),
                    updatedAt: new Date().toISOString(),
                    likesCount: 0,
                    commentsCount: 0,
                    sharesCount: 0,
                    likes: []
                }
            );

            // Update original post shares count
            const originalPostRef = this.functions.doc(this.db, 'posts', originalPostId);
            await this.functions.updateDoc(originalPostRef, {
                sharesCount: this.functions.increment(1),
                updatedAt: new Date().toISOString()
            });

            return { success: true, id: shareRef.id };
        } catch (error) {
            console.error('Error sharing post:', error);
            return { success: false, error: error.message };
        }
    }

    // Delete post
    async deletePost(postId, userId) {
        try {
            const postRef = this.functions.doc(this.db, 'posts', postId);
            const postDoc = await this.functions.getDoc(postRef);

            if (!postDoc.exists()) {
                return { success: false, error: 'Post not found' };
            }

            const postData = postDoc.data();
            if (postData.authorId !== userId) {
                return { success: false, error: 'Unauthorized' };
            }

            await this.functions.updateDoc(postRef, {
                isActive: false,
                deletedAt: new Date().toISOString()
            });

            return { success: true };
        } catch (error) {
            console.error('Error deleting post:', error);
            return { success: false, error: error.message };
        }
    }

    // Real-time listener for posts
    listenToPosts(callback, limitCount = 20) {
        const q = this.functions.query(
            this.functions.collection(this.db, 'posts'),
            this.functions.where('isActive', '==', true),
            this.functions.orderBy('createdAt', 'desc'),
            this.functions.limit(limitCount)
        );

        return this.functions.onSnapshot(q, (querySnapshot) => {
            const posts = [];
            querySnapshot.forEach((doc) => {
                posts.push({ id: doc.id, ...doc.data() });
            });
            callback(posts);
        });
    }
}

// Initialize the service
window.newsFeedService = new NewsFeedService();

console.log('News Feed Firebase service initialized');
