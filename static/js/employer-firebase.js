// Employer Firebase operations
class EmployerFirebaseService {
    constructor() {
        this.db = window.firebaseDB;
        this.auth = window.firebaseAuth;
        this.storage = window.firebaseStorage;
        this.functions = window.firestoreFunctions;
        this.authFunctions = window.authFunctions;
        this.storageFunctions = window.storageFunctions;
    }

    // Create employer account
    async createEmployer(employerData) {
        try {
            const docRef = await this.functions.addDoc(
                this.functions.collection(this.db, 'employers'), 
                {
                    ...employerData,
                    createdAt: new Date().toISOString(),
                    isActive: true
                }
            );
            return { success: true, id: docRef.id };
        } catch (error) {
            console.error('Error creating employer:', error);
            return { success: false, error: error.message };
        }
    }

    // Get all employers
    async getEmployers() {
        try {
            const querySnapshot = await this.functions.getDocs(
                this.functions.collection(this.db, 'employers')
            );
            const employers = [];
            querySnapshot.forEach((doc) => {
                employers.push({ id: doc.id, ...doc.data() });
            });
            return { success: true, data: employers };
        } catch (error) {
            console.error('Error getting employers:', error);
            return { success: false, error: error.message };
        }
    }

    // Get employer by ID
    async getEmployerById(employerId) {
        try {
            const docRef = this.functions.doc(this.db, 'employers', employerId);
            const docSnap = await this.functions.getDoc(docRef);
            
            if (docSnap.exists()) {
                return { success: true, data: { id: docSnap.id, ...docSnap.data() } };
            } else {
                return { success: false, error: 'Employer not found' };
            }
        } catch (error) {
            console.error('Error getting employer:', error);
            return { success: false, error: error.message };
        }
    }

    // Update employer
    async updateEmployer(employerId, updateData) {
        try {
            const docRef = this.functions.doc(this.db, 'employers', employerId);
            await this.functions.updateDoc(docRef, {
                ...updateData,
                updatedAt: new Date().toISOString()
            });
            return { success: true };
        } catch (error) {
            console.error('Error updating employer:', error);
            return { success: false, error: error.message };
        }
    }

    // Create job posting
    async createJob(jobData) {
        try {
            const docRef = await this.functions.addDoc(
                this.functions.collection(this.db, 'jobs'), 
                {
                    ...jobData,
                    postedAt: new Date().toISOString(),
                    isActive: true,
                    applicationsCount: 0
                }
            );
            return { success: true, id: docRef.id };
        } catch (error) {
            console.error('Error creating job:', error);
            return { success: false, error: error.message };
        }
    }

    // Get jobs by employer
    async getJobsByEmployer(employerId) {
        try {
            const q = this.functions.query(
                this.functions.collection(this.db, 'jobs'),
                this.functions.where('employerId', '==', employerId),
                this.functions.orderBy('postedAt', 'desc')
            );
            
            const querySnapshot = await this.functions.getDocs(q);
            const jobs = [];
            querySnapshot.forEach((doc) => {
                jobs.push({ id: doc.id, ...doc.data() });
            });
            return { success: true, data: jobs };
        } catch (error) {
            console.error('Error getting jobs:', error);
            return { success: false, error: error.message };
        }
    }

    // Get all jobs
    async getAllJobs() {
        try {
            const q = this.functions.query(
                this.functions.collection(this.db, 'jobs'),
                this.functions.where('isActive', '==', true),
                this.functions.orderBy('postedAt', 'desc')
            );
            
            const querySnapshot = await this.functions.getDocs(q);
            const jobs = [];
            querySnapshot.forEach((doc) => {
                jobs.push({ id: doc.id, ...doc.data() });
            });
            return { success: true, data: jobs };
        } catch (error) {
            console.error('Error getting all jobs:', error);
            return { success: false, error: error.message };
        }
    }

    // Update job
    async updateJob(jobId, updateData) {
        try {
            const docRef = this.functions.doc(this.db, 'jobs', jobId);
            await this.functions.updateDoc(docRef, {
                ...updateData,
                updatedAt: new Date().toISOString()
            });
            return { success: true };
        } catch (error) {
            console.error('Error updating job:', error);
            return { success: false, error: error.message };
        }
    }

    // Delete job
    async deleteJob(jobId) {
        try {
            const docRef = this.functions.doc(this.db, 'jobs', jobId);
            await this.functions.updateDoc(docRef, {
                isActive: false,
                deletedAt: new Date().toISOString()
            });
            return { success: true };
        } catch (error) {
            console.error('Error deleting job:', error);
            return { success: false, error: error.message };
        }
    }

    // Create application
    async createApplication(applicationData) {
        try {
            const docRef = await this.functions.addDoc(
                this.functions.collection(this.db, 'applications'), 
                {
                    ...applicationData,
                    appliedAt: new Date().toISOString(),
                    status: 'pending'
                }
            );
            return { success: true, id: docRef.id };
        } catch (error) {
            console.error('Error creating application:', error);
            return { success: false, error: error.message };
        }
    }

    // Get applications by employer
    async getApplicationsByEmployer(employerId) {
        try {
            const q = this.functions.query(
                this.functions.collection(this.db, 'applications'),
                this.functions.where('employerId', '==', employerId),
                this.functions.orderBy('appliedAt', 'desc')
            );
            
            const querySnapshot = await this.functions.getDocs(q);
            const applications = [];
            querySnapshot.forEach((doc) => {
                applications.push({ id: doc.id, ...doc.data() });
            });
            return { success: true, data: applications };
        } catch (error) {
            console.error('Error getting applications:', error);
            return { success: false, error: error.message };
        }
    }

    // Update application status
    async updateApplicationStatus(applicationId, status) {
        try {
            const docRef = this.functions.doc(this.db, 'applications', applicationId);
            await this.functions.updateDoc(docRef, {
                status: status,
                updatedAt: new Date().toISOString()
            });
            return { success: true };
        } catch (error) {
            console.error('Error updating application status:', error);
            return { success: false, error: error.message };
        }
    }
}

// Initialize the service
window.employerFirebaseService = new EmployerFirebaseService();

console.log('Employer Firebase service initialized');
