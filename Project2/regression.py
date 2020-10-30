import numpy as np
from numpy import random
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error
from functions import FrankeFunction,X_D
from sklearn.utils import resample
import matplotlib.pyplot as plt
from data_prep import data_prep
import seaborn as sb


class regression:
    def __init__(self, X_train, X_test, z_train, z_test):
        self.weights = None
        self.X_test = X_test
        self.X_train = X_train
        self.z_test = z_test
        self.z_train = z_train




    def SGD(self, epochs, mini_batch_size, t0, t1, gamma=0, lam=0):
        """
        lam != 0 represents ridge method
        """
        m = len(self.z_train)
        d = self.X_train.shape[1]
        self.weights = random.randn(d)
        def learning_schedule(t):
            if t0 == 0:
                return 0.00001
            else:
                return t0/(t1+t)#t0/(t1+0.000005*t)
        MSE_array = np.ones(epochs)*np.nan
        ind = np.arange(0,m)
        v = 0
        for i in range(epochs):
            random.shuffle(ind)
            X_train_shuffle = self.X_train[ind]
            z_train_shuffle = self.z_train[ind]
            for j in range(0,m,mini_batch_size):
                z_tilde = X_train_shuffle[j:j+mini_batch_size] @ self.weights
                diff_vec = z_tilde - z_train_shuffle[j:j+mini_batch_size]
                gradient = 2*(X_train_shuffle[j:j+mini_batch_size].T @ diff_vec)/mini_batch_size + 2*lam*self.weights
                eta = learning_schedule(i*m+j)
                v = gamma*v + eta*gradient
                self.weights = self.weights - v
            z_pred = X_train@self.weights
            MSE_array[i] = mean_squared_error(self.z_train, z_pred)
        self.MSE = mean_squared_error(self.z_train, z_pred)
        #plt.plot(MSE_array, '.')
        #plt.xlabel("epoch")
        #plt.ylabel("MSE")
        #plt.show()
        #print(z_pred)
        #print(self.z_train)

    def OLS(self):
        self.weights = np.linalg.pinv(self.X_train.T.dot(self.X_train)).dot(self.X_train.T).dot(self.z_train)
        z_pred = self.X_test @ self.weights
        self.MSE = mean_squared_error(self.z_test, z_pred)

    def ridge(self, hyp):
        I = np.identity(self.X_train.shape[1])
        self.weights = np.linalg.pinv(self.X_train.T.dot(self.X_train)-hyp*I).dot(self.X_train.T).dot(self.z_train)
        z_pred = self.X_test @ self.weights
        self.MSE = mean_squared_error(self.z_test, z_pred)






if __name__ == '__main__':
    np.random.seed(100)

    n = 100
    noise = 0.1
    x = np.random.uniform(0,1,n)
    y = np.random.uniform(0,1,n)
    x,y = np.meshgrid(x,y) + noise*np.random.randn(n,n)
    z = np.ravel(FrankeFunction(x,y))

    data = data_prep(x,y,z,10)
    X_train, X_test, z_train, z_test = data()
    my_instance = regression(X_train, X_test, z_train, z_test)

    # doing SGD regression on our object
    my_instance.SGD(epochs=200, mini_batch_size=30, t0=0, t1=1, gamma = 0.9, lam = 0)
    print("MSE from SGD (OLS):                  ",my_instance.MSE)

    # doing OLS regression on our object
    my_instance.OLS()
    print("MSE from OLS:                        ",my_instance.MSE, "\n")

    hyp1 = 0.1
    hyp2 = 0.01
    hyp3 = 0.001
    my_instance.SGD(epochs=200, mini_batch_size=30, t0=0, t1=1, gamma = 0.9, lam=hyp1)
    print("MSE from SGD (Ridge, hyp=%.0e):     " % hyp1, my_instance.MSE)
    my_instance.ridge(hyp1)
    print("MSE from Ridge (hyp=%.0e):          " % hyp1, my_instance.MSE, "\n")

    my_instance.SGD(epochs=200, mini_batch_size=30, t0=0, t1=1, gamma = 0.9, lam=hyp2)
    print("MSE from SGD (Ridge, hyp=%.0e):     " % hyp2, my_instance.MSE)
    my_instance.ridge(hyp2)
    print("MSE from Ridge (hyp=%.0e):          " % hyp2, my_instance.MSE, "\n")

    my_instance.SGD(epochs=200, mini_batch_size=30, t0=0, t1=1, gamma = 0.9, lam=hyp3)
    print("MSE from SGD (Ridge, hyp=%.0e):     " % hyp3, my_instance.MSE)
    my_instance.ridge(hyp3)
    print("MSE from Ridge (hyp=%.0e):          " % hyp3, my_instance.MSE, "\n")



    """
    Making a heatmap of MSE with SGD as function of epochs and mini batch size.
    Learning rate is constant.
    """
    create_heatmap_MSE = False
    if create_heatmap_MSE == True:
        epochs = np.linspace(20, 300, 15).astype("int")
        mb_sizes = np.linspace(5, 25, 5).astype("int")

        MSE_SGD = np.zeros((len(epochs), len(mb_sizes)))
        MSE_SGD_r1 = np.zeros((len(epochs), len(mb_sizes)))
        MSE_SGD_r2 = np.zeros((len(epochs), len(mb_sizes)))
        MSE_SGD_r3 = np.zeros((len(epochs), len(mb_sizes)))
        for i, ep in enumerate(epochs):
            for j, mbs in enumerate(mb_sizes):
                 my_instance.SGD(epochs=ep, mini_batch_size=mbs, t0=0, t1=1, gamma=0.9, lam=0)
                 MSE_SGD[i,j] = my_instance.MSE

                 my_instance.SGD(epochs=ep, mini_batch_size=mbs, t0=0, t1=1, gamma=0.9, lam=hyp1)
                 MSE_SGD_r1[i,j] = my_instance.MSE

                 my_instance.SGD(epochs=ep, mini_batch_size=mbs, t0=0, t1=1, gamma=0.9, lam=hyp2)
                 MSE_SGD_r2[i,j] = my_instance.MSE

                 my_instance.SGD(epochs=ep, mini_batch_size=mbs, t0=0, t1=1, gamma=0.9, lam=hyp3)
                 MSE_SGD_r3[i,j] = my_instance.MSE
                 print("Epoch: %i/%i      Mini batch size: %i/%i   " % (ep, epochs[-1], mbs, mb_sizes[-1]), end="\r")

        plt.figure("OLS")
        heatmap = sb.heatmap(MSE_SGD, annot=True,cmap="viridis_r", xticklabels=mb_sizes, yticklabels=epochs, cbar_kws={'label': 'Mean squared error'}, fmt = ".5")
        heatmap.set_xlabel("Mini batch size")
        heatmap.set_ylabel("Epochs")
        heatmap.invert_yaxis()
        heatmap.set_title("Heatmap of MSE using SGD (OLS)")
        fig = heatmap.get_figure()
        fig.savefig("./figures/SGD_MSE_heatmap_OLS.jpg",bbox_inches='tight', pad_inches=0.1, dpi=1200)

        plt.figure("Ridge1")
        heatmap_r = sb.heatmap(MSE_SGD_r1, annot=True,cmap="viridis_r", xticklabels=mb_sizes, yticklabels=epochs, cbar_kws={'label': 'Mean squared error'}, fmt = ".5")
        heatmap_r.set_xlabel("Mini batch size")
        heatmap_r.set_ylabel("Epochs")
        heatmap_r.invert_yaxis()
        heatmap_r.set_title("Heatmap of MSE using SGD (Ridge, $\lambda$=%s)" % hyp1)
        fig = heatmap_r.get_figure()
        fig.savefig("./figures/SGD_MSE_heatmap_ridge_%s.jpg" % hyp1,bbox_inches='tight',pad_inches=0.1, dpi=1200)

        plt.figure("Ridge2")
        heatmap_r = sb.heatmap(MSE_SGD_r2, annot=True,cmap="viridis_r", xticklabels=mb_sizes, yticklabels=epochs, cbar_kws={'label': 'Mean squared error'}, fmt = ".5")
        heatmap_r.set_xlabel("Mini batch size")
        heatmap_r.set_ylabel("Epochs")
        heatmap_r.invert_yaxis()
        heatmap_r.set_title("Heatmap of MSE using SGD (Ridge, $\lambda$=%s)" % hyp2)
        fig = heatmap_r.get_figure()
        fig.savefig("./figures/SGD_MSE_heatmap_ridge_%s.jpg" % hyp2,bbox_inches='tight',pad_inches=0.1, dpi=1200)

        plt.figure("Ridge3")
        heatmap_r = sb.heatmap(MSE_SGD_r3, annot=True,cmap="viridis_r", xticklabels=mb_sizes, yticklabels=epochs, cbar_kws={'label': 'Mean squared error'}, fmt = ".5")
        heatmap_r.set_xlabel("Mini batch size")
        heatmap_r.set_ylabel("Epochs")
        heatmap_r.invert_yaxis()
        heatmap_r.set_title("Heatmap of MSE using SGD (Ridge, $\lambda$=%s)" % hyp3)
        fig = heatmap_r.get_figure()
        fig.savefig("./figures/SGD_MSE_heatmap_ridge_%s.jpg" % hyp3,bbox_inches='tight',pad_inches=0.1, dpi=1200)

        plt.show()


    """
    Using the optimal values for epochs and mini batch size from the heatmap to
    estimate the optimal learning rate based on t0 and t1.
    """
    create_heatmap_lr = True
    if create_heatmap_lr == True:
        # the number of epochs highly affects the computation time
        epoch = 60                     # estimated best value from OLS heatmap above
        mbs = 5                        # estimated best value from OLS heatmap above
        epoch_r1 = 60                   # estimated best value from Ridge heatmap above
        epoch_r2 = 120                   # estimated best value from Ridge heatmap above
        epoch_r3 = 100                   # estimated best value from Ridge heatmap above
        mbs_r1 = 5                     # estimated best value from Ridge heatmap above
        mbs_r2 = 5                      # estimated best value from Ridge heatmap above
        mbs_r3 = 5                      # estimated best value from Ridge heatmap above

        #t0s = np.linspace(0.01, 0.55, 6)#.astype("int")
        #t0s = ((100*t0s).astype("int"))/100 # got loads of decimals for some reason. This line fixes it
        #t1s = np.linspace(60, 200, 8).astype("int")

        t0s = np.linspace(0.05, 0.5, 5)#.astype("int")
        #t0s = ((100*t0s).astype("int"))/100 # got loads of decimals for some reason. This line fixes it
        t1s = np.linspace(100, 5000, 5).astype("int")

        MSE_lr = np.zeros((len(t1s), len(t0s)))
        MSE_lr_r1 = np.zeros((len(t1s), len(t0s)))
        MSE_lr_r2 = np.zeros((len(t1s), len(t0s)))
        MSE_lr_r3 = np.zeros((len(t1s), len(t0s)))
        for i, t0 in enumerate(t0s):
            for j, t1 in enumerate(t1s):
                 my_instance.SGD(epochs=epoch, mini_batch_size=mbs, t0=t0, t1=t1, gamma=0.9, lam=0)
                 MSE_lr[j,i] = my_instance.MSE

                 my_instance.SGD(epochs=epoch_r1, mini_batch_size=mbs_r1, t0=t0, t1=t1, gamma=0.9, lam=hyp1)
                 MSE_lr_r1[j,i] = my_instance.MSE

                 my_instance.SGD(epochs=epoch_r2, mini_batch_size=mbs_r2, t0=t0, t1=t1, gamma=0.9, lam=hyp2)
                 MSE_lr_r2[j,i] = my_instance.MSE

                 my_instance.SGD(epochs=epoch_r3, mini_batch_size=mbs_r3, t0=t0, t1=t1, gamma=0.9, lam=hyp3)
                 MSE_lr_r3[j,i] = my_instance.MSE
                 print("t0: %s/%s      t1: %i/%i     " % (t0, t0s[-1], t1, t1s[-1]), end="\r")

        MSE_max = np.where(MSE_lr > 1)
        MSE_max_r1 = np.where(MSE_lr_r1 > 1)
        MSE_max_r2 = np.where(MSE_lr_r2 > 1)
        MSE_max_r3 = np.where(MSE_lr_r3 > 1)
        MSE_lr[MSE_max] = 1
        MSE_lr_r1[MSE_max_r1] = 1
        MSE_lr_r2[MSE_max_r2] = 1
        MSE_lr_r3[MSE_max_r3] = 1


        plt.figure("OLS")
        heatmap = sb.heatmap(MSE_lr, annot=True,cmap="viridis_r", xticklabels=t0s, yticklabels=t1s, cbar_kws={'label': 'Mean squared error'}, fmt = ".4")
        heatmap.set_xlabel("t1")
        heatmap.set_ylabel("t0")
        heatmap.invert_yaxis()
        heatmap.set_title("MSE of learning rate (OLS, epoch=%i, batch=%i)" % (epoch,mbs))
        fig = heatmap.get_figure()
        fig.savefig("./figures/Learning_rate_MSE_heatmap_OLS.jpg", bbox_inches='tight', pad_inches=0.1, dpi=1200)

        plt.figure("Ridge1")
        heatmap_r = sb.heatmap(MSE_lr_r1, annot=True,cmap="viridis_r", xticklabels=t0s, yticklabels=t1s, cbar_kws={'label': 'Mean squared error'}, fmt = ".4")
        heatmap_r.set_xlabel("t1")
        heatmap_r.set_ylabel("t0")
        heatmap_r.invert_yaxis()
        heatmap_r.set_title("MSE of learning rate(Ridge, $\lambda$=%s, epoch=%i, batch=%i)" % (hyp1,epoch_r1,mbs_r1))
        fig = heatmap_r.get_figure()
        fig.savefig("./figures/Learning_rate_MSE_heatmap_ridge_%s.jpg" % hyp1, bbox_inches='tight', pad_inches=0.1, dpi=1200)

        plt.figure("Ridge2")
        heatmap_r = sb.heatmap(MSE_lr_r2, annot=True,cmap="viridis_r", xticklabels=t0s, yticklabels=t1s, cbar_kws={'label': 'Mean squared error'}, fmt = ".4")
        heatmap_r.set_xlabel("t1")
        heatmap_r.set_ylabel("t0")
        heatmap_r.invert_yaxis()
        heatmap_r.set_title("MSE of learning rate(Ridge, $\lambda$=%s, epoch=%i, batch=%i)" % (hyp2,epoch_r2,mbs_r2))
        fig = heatmap_r.get_figure()
        fig.savefig("./figures/Learning_rate_MSE_heatmap_ridge_%s.jpg" % hyp2, bbox_inches='tight', pad_inches=0.1, dpi=1200)

        plt.figure("Ridge3")
        heatmap_r = sb.heatmap(MSE_lr_r3, annot=True,cmap="viridis_r", xticklabels=t0s, yticklabels=t1s, cbar_kws={'label': 'Mean squared error'}, fmt = ".4")
        heatmap_r.set_xlabel("t1")
        heatmap_r.set_ylabel("t0")
        heatmap_r.invert_yaxis()
        heatmap_r.set_title("MSE of learning rate(Ridge, $\lambda$=%s, epoch=%i, batch=%i)" % (hyp3,epoch_r3,mbs_r3))
        fig = heatmap_r.get_figure()
        fig.savefig("./figures/Learning_rate_MSE_heatmap_ridge_%s.jpg" % hyp3, bbox_inches='tight', pad_inches=0.1, dpi=1200)

        plt.show()




#
