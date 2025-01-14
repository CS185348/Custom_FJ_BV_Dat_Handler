import datetime
from cmath import nan
from difflib import Match
from logging import raiseExceptions
from ssl import SSL_ERROR_SSL
from tkinter import Y
import enum
from cv2 import sqrt
import _3DVisLabLib
import json
import cv2
import random
from statistics import mean 
import copy
import random
import time
import multiprocessing
import statistics
import scipy
import math
import numpy as np
from scipy import stats
from scipy.stats import skew
import gc
import MatchImages_lib
import copyreg#need this to pickle keypoints
#gc.disable()
import psutil
import os
from sklearn.decomposition import PCA

#stuff for HOG
#from skimage.io import Ski_imread, ski_imshow
#from skimage.transform import ski_resize
#from skimage.feature import ski_hog
#from skimage import ski_exposure


import matplotlib
#matplotlib.use('Agg')#can get "Tcl_AsyncDelete: async handler deleted by the wrong thread" crashes otherwise
import matplotlib.pyplot as plt
def HM_data_MetricDistances():
    print("plop")

def PlotAndSave_2datas(Title,Filepath,Data1):
    
    #this causes crashes
    #save out plot of 1D data
    try:
        #Data1=np.random.rand(30,22)
        plt.pcolormesh((Data1), cmap = 'autumn')
        #plt.plot(Data1,Data2,'bo')#bo will draw dots instead of connected line
        plt.ylabel(Title)
        #plt.ylim([0, max(Data1)])
        #plt.ylim([0, max(Data2)])
        plt.savefig(Filepath)
        plt.cla()
        plt.clf()
        plt.close()
    except Exception as e:
        print("Error with matpyplot",e)

class MatchImagesObject():
    
    def ForceNormalise_forHOG(self,image1):
        #TODO cannot figure out why normal normalising makes this (visibly) normalised
        #while other methods leave it blown out - it may not be significant statistically but
        #it would help with visualising the process 
        image1_Norm = cv2.normalize(image1, image1,0, 255, cv2.NORM_MINMAX)
        image2_Norm = cv2.normalize(image1,image1, 0, 255, cv2.NORM_MINMAX)
        # black blank image, hieght of both images and width of widest image
        blank_image = np.zeros(shape=[image1.shape[0]+image1.shape[0], max(image1.shape[1],image1.shape[1]), image1.shape[2]], dtype=np.uint8)
        #drop in images
        blank_image[0:image1_Norm.shape[0],0:image1_Norm.shape[1],:]=image1_Norm[:,:,:]
        blank_image[image1_Norm.shape[0]:,0:image2_Norm.shape[1]:,:]=image2_Norm[:,:,:]
        blank_image=blank_image[0:image1_Norm.shape[0],0:image1_Norm.shape[1],:]
        #_3DVisLabLib.ImageViewer_Quick_no_resize(cv2.resize(blank_image,(blank_image.shape[1]*3,blank_image.shape[0]*3)),0,True,True)
        return blank_image

    def StackTwoimages(self,image1,image2):
        #if grayscale-convert to colour
        if len(image1.shape)!=3:
            image1 = cv2.cvtColor(image1,cv2.COLOR_GRAY2RGB)
        if len(image2.shape)!=3:
            image2 = cv2.cvtColor(image2,cv2.COLOR_GRAY2RGB)
        image1_Norm = cv2.normalize(image1, image1,0, 255, cv2.NORM_MINMAX)
        image2_Norm = cv2.normalize(image2,image2, 0, 255, cv2.NORM_MINMAX)
        # black blank image, hieght of both images and width of widest image
        blank_image = np.zeros(shape=[image1.shape[0]+image2.shape[0], max(image1.shape[1],image2.shape[1]), image2.shape[2]], dtype=np.uint8)
        #drop in images
        blank_image[0:image1_Norm.shape[0],0:image1_Norm.shape[1],:]=image1_Norm[:,:,:]
        blank_image[image1_Norm.shape[0]:,0:image2_Norm.shape[1]:,:]=image2_Norm[:,:,:]
        #_3DVisLabLib.ImageViewer_Quick_no_resize(cv2.resize(blank_image,(blank_image.shape[1]*3,blank_image.shape[0]*3)),0,True,True)
        return blank_image

    def USERFunction_PrepareForHOG(self,image,TargetHeight_HOG=64,TargetWidth_HOG=128):
        #HOG expects 64 * 128
        #lets not chagne aspect ratio
        ImageHeight=image.shape[0]
        ImageWidth=image.shape[1]
        #set to target height then crop as needed
        Percent2match=TargetHeight_HOG/ImageHeight
        TargetWidth=round(ImageWidth*Percent2match)
        Resized=cv2.resize(image,(TargetWidth,TargetHeight_HOG))

        #create blank
        blank_image = np.zeros(shape=[TargetHeight_HOG, TargetWidth_HOG, image.shape[2]], dtype=np.uint8)

        #now crop to HOG shape
        HOG_specific_crop=Resized[:,0:TargetWidth_HOG,:]

        blank_image[0:HOG_specific_crop.shape[0],0:HOG_specific_crop.shape[1],:]=HOG_specific_crop

        #now need to flip on its side
        # rotate ccw
        Rotate=cv2.transpose(blank_image)
        Rotate=cv2.flip(Rotate,flipCode=0)
        return Rotate

    def USERFunction_CropForFM(self,image):
        return image
        #return image[:,0:151,:]
        #return image[0:int(image.shape[0]/1.1),0:int(image.shape[1]/1),:]
    def USERFunction_CropForHistogram(self,image):
        return image
        #return image[:,0:151,:]
    def USERFunction_OriginalImage(self,image):
        return image
        return cv2.resize(image.copy(),(500,250))

    def USERFunction_Crop_Pixels(self,image,CropRangeY,CropRangeX):
        if len(image.shape)!=3:
            return image[CropRangeY[0]:CropRangeY[1],CropRangeX[0]:CropRangeX[1]]
        else:
            return image[CropRangeY[0]:CropRangeY[1],CropRangeX[0]:CropRangeX[1],:]

    def USERFunction_ResizePercent(self,image,Percent):
        Percent=Percent/100
        return cv2.resize(image.copy(),(int(image.shape[1]*Percent),int(image.shape[0]*Percent)))

    def USERFunction_Resize(self,image):

        #height/length
        #return image
        # if len(image.shape)!=3:
        # #return image
        #     return cv2.resize(image.copy(),(300,200))
        # else:
        #     return cv2.resize(image.copy(),(300,200))
        return image

        #usual for mm1 side
        #grayscale image
        if len(image.shape)!=3:
        #return image
            return image[0:62,0:130]
        else:
            return image[0:62,0:130,:]
            #image= image[303:800,400:1500,:]
            image=cv2.resize(image,(500,250))
            return image
        #this is pixels not percentage!
        #return image
        #return cv2.resize(image.copy(),(300,200))

    class ProcessTerms(enum.Enum):
        Sequential="Sequential"
        DoubleUp="DoubleUp"

    """Class to hold information for image sorting & match process"""
    def __init__(self):
        #USER VARS
        #self.InputFolder=r"E:\NCR\TestImages\Faces\img_align_celeba"
        #self.InputFolder=r"E:\NCR\TestImages\Goodfellas_longshot_Random"
        #self.InputFolder=r"E:\NCR\TestImages\UK_SMall"
        #self.InputFolder=r"E:\NCR\TestImages\UK_1000"
        #self.InputFolder=r"E:\NCR\TestImages\Faces\randos"
        #self.InputFolder=r"E:\NCR\TestImages\UK_Side_SMALL_15sets10"
        self.InputFolder=r"E:\NCR\TestImages\Faces\img_align_celeba"
        #self.InputFolder=r"E:\NCR\TestImages\MixedSets_side"
        
        self.Outputfolder=r"E:\NCR\TestImages\MatchOutput"
        self.SubSetOfData=int(4500)#subset of data
        self.MemoryError_ReduceLoad=(True,10)#fix memory errors (multiprocess makes copies of everything) (Activation,N+1 cores to use -EG use 4 cores = (True,5))
        self.BeastMode=False# Beast mode will optimise processing and give speed boost - but won't be able to update user with estimated time left
        #self.OutputImageOrganisation=self.ProcessTerms.Sequential.value
        self.HyperThreading=True#Experimental - hyperthreads are virtual cores - so if you see multiprocesses not maxed out for their
        #share of CPU - potentially this might mean they could be hyperthreaded - but feature matching may not work as well like this if
        #enabled.. needs more testing - also lots of threads will blow out the memory
        #internal variables
        self.FreeMemoryBuffer_pc=25#how much memory % should be reserved while processing

        self.TraceExtractedImg_to_DatRecord="TraceImg_to_DatRecord.json"
        self.OutputPairs=self.Outputfolder + "\\Pairs\\"
        self.OutputDuplicates=self.Outputfolder + "\\Duplicates\\"
        self.ImagesInMem_Pairing=dict()
        self.GetDuplicates=False
        self.startTime =None
        self.Endtime =None
        self.HM_data_MetricDistances=None
        self.HM_data_MetricDistances_auto=None
        self.DummyMinValue=-9999923
        self.MetricDictionary=dict()
        self.TraceExtractedImg_to_DatRecordObj=None
        self.ImagesInMem_to_Process=dict()
        self.DuplicatesToCheck=dict()
        self.DuplicatesFound=[]
        self.Mean_Std_Per_cyclelist=None
        self.HistogramSelfSimilarityThreshold=0.005#should be zero but incase there is image compression noise
        self.CurrentBaseImage=None
        
        #populatemetricDictionary
        self.Metrics_dict=dict()

        #self.Metrics_dict["HM_data_FM"]=None#slow - maybe cant be hyperthreaded?
        self.Metrics_dict["HM_data_histo"]=None#fast =no idea about hyperthreading
        #self.Metrics_dict["HM_data_FourierDifference"]=None#fast -hyperthreading yes
        #self.Metrics_dict["HM_data_PhaseCorrelation"]=None #-hyperthreading yes
        self.Metrics_dict["HM_data_HOG_Dist"]=None#slow -hyperthreading yes
        #self.Metrics_dict["HM_data_EigenVectorDotProd"]=None#fast
        self.Metrics_dict["HM_data_EigenValueDifference"]=None#fast #-hyperthreading yes
        self.Metrics_dict["HM_data_FourierPowerDensity"]=None#fast #-hyperthreading yes
    class FeatureMatch_Dict_Common:

        SIFT_default=dict(nfeatures=0,nOctaveLayers=3,contrastThreshold=0.04,edgeThreshold=10)
        
        ORB_default=dict(nfeatures=20000,scaleFactor=1.3,
                        nlevels=2,edgeThreshold=0,
                        firstLevel=0, WTA_K=2,
                        scoreType=0,patchSize=155)
        
        SIFT_Testing=dict(nfeatures=50,contrastThreshold=0.04,edgeThreshold=10)
        
        ORB_Testing=dict(nfeatures=20000,scaleFactor=1.02,
                        nlevels=4,edgeThreshold=0,
                        firstLevel=4, WTA_K=2,
                        scoreType=0,patchSize=100)

    class ImageInfo():
        def __init__(self):
            self.Histogram=None
            self.OriginalImage=None
            self.ImageColour=None
            self.ImageAdjusted=None
            self.FM_Keypoints=None
            self.FM_Descriptors=None
            self.FourierTransform_mag=None
            self.ImageGrayscale=None
            self.EigenValues=None
            self.EigenVectors=None
            self.PrincpleComponents=None
            self.HOG_Mag=None
            self.HOG_Angle=None
            self.OPENCV_hog_descriptor=None
            self.PhaseCorrelate_FourierMagImg=None
            self.DebugImage=None
            self.OriginalImageFilePath=None
            self.PwrSpectralDensity=None
            
def PlotAndSave(Title,Filepath,Data,maximumvalue):
    
    #this causes crashes
    #save out plot of 1D data
    try:
        plt.plot(Data)
        plt.ylabel(Title)
        plt.ylim([0, maximumvalue])
        plt.savefig(Filepath)
        plt.cla()
        plt.clf()
        plt.close()
    except Exception as e:
        print("Error with matpyplot",e)

def PlotAndSaveHistogram(Title,Filepath,Data,maximumvalue,bins):
    #(skew(x))
    try:
        plt.hist(Data, bins = bins)
        #plt.ylabel(Title)
        plt.xlim([0, 2])
        plt.savefig(Filepath)
        plt.cla()
        plt.clf()
        plt.close()
    except Exception as e:
        print("Error with matpyplot",e)


def GetAverageOfMatches(List,Span):
    Spanlist=List[0:Span]
    Distances=[]
    for elem in Spanlist:
        Distances.append(elem.distance)
    return round(mean(Distances),2)

def normalize_2d(matrix):
    #check the matrix isnt all same number
    if matrix.min()==0 and matrix.max()==0:
        print("WARNING, matrix all zeros")
        return matrix
    if matrix.max()==matrix.min():
        print("WARNING: matrix homogenous")
        return np.ones(matrix.shape)
    return (matrix - np.min(matrix)) / (np.max(matrix) - np.min(matrix))



def _pickle_keypoints(point):
    return cv2.KeyPoint, (*point.pt, point.size, point.angle,
                          point.response, point.octave, point.class_id)




def main():
    #create resource manager
    PrepareMatchImages=MatchImagesObject()
    #delete all files in folder
    print("Delete output folders:\n",PrepareMatchImages.Outputfolder)
    if _3DVisLabLib.yesno("?"):
        _3DVisLabLib.DeleteFiles_RecreateFolder(PrepareMatchImages.Outputfolder)
        #make subfolders
        _3DVisLabLib. MakeFolder( PrepareMatchImages.OutputPairs)
        _3DVisLabLib. MakeFolder(PrepareMatchImages.OutputDuplicates)

    #ask if user wants to check for duplicates
    print("Get duplicates only?? - this will be in ~o^(2/N) complexity time (very long)!!!")
    PrepareMatchImages.GetDuplicates= _3DVisLabLib.yesno("?")

    #get all files in input folder
    InputFiles=_3DVisLabLib.GetAllFilesInFolder_Recursive(PrepareMatchImages.InputFolder)

    #filter out non images
    ListAllImages=_3DVisLabLib.GetList_Of_ImagesInList(InputFiles)


    #get object that links images to dat records
    print("attempting to load image to dat record trace file",PrepareMatchImages.InputFolder + "\\" + PrepareMatchImages.TraceExtractedImg_to_DatRecord)
    try:
        Json_to_load=PrepareMatchImages.InputFolder + "\\" + PrepareMatchImages.TraceExtractedImg_to_DatRecord
        with open(Json_to_load) as json_file:
            PrepareMatchImages.TraceExtractedImg_to_DatRecordObj = json.load(json_file)
            print("json loaded succesfully")
            PrepareMatchImages.TraceExtractedImg_to_DatRecordObj
    except Exception as e:
        print("JSON_Open error attempting to open json file " + str(PrepareMatchImages.InputFolder + "\\" + PrepareMatchImages.TraceExtractedImg_to_DatRecord) + " " + str(e))
        if _3DVisLabLib.yesno("Continue operation? No image to dat record trace will be possible so only image matching & sorting")==False:
            raise Exception("User declined to continue after JSOn image vs dat record file not found")
    #start timer
    PrepareMatchImages.startTime=time.time()

    #load images in random order for testing
    randomdict=dict()
    for Index, ImagePath in enumerate(ListAllImages):
        randomdict[ImagePath]=Index

    #user may have specified a subset of data
    RandomOrder=[]
    while (len(RandomOrder)<PrepareMatchImages.SubSetOfData) and (len(randomdict)>0):
        randomchoice_img=random.choice(list(randomdict.keys()))
        RandomOrder.append(randomchoice_img)
        del randomdict[randomchoice_img]
    print("User image reduction, operating on with",len(RandomOrder)," from ",len(ListAllImages),"images")
    #populate images 
    #load images into memory

    # Create HOG Descriptor object outside of loops
    HOG_extrator = cv2.HOGDescriptor()
    #record images to allow us to debug code
    ImageReviewDict=dict()
    for Index, ImagePath in enumerate(RandomOrder):
        if Index%30==0: print("Image load",Index,"/",len(RandomOrder))

        if True==True:
        #try:
            ImageInfo=MatchImages_lib.PrepareImageMetrics_Faces(PrepareMatchImages,ImagePath,Index,ImageReviewDict,HOG_extrator)
            
            #populate dictionary
            PrepareMatchImages.ImagesInMem_to_Process[ImagePath]=(ImageInfo)
            
        #except:
        #    print("error with image, skipping",ImagePath)

    #need this to copy the keypoints for some reason - incompatible with pickle which means
    #any multiprocessing wont work either
    copyreg.pickle(cv2.KeyPoint().__class__, _pickle_keypoints)
    #need this test to see if we can pickle the object - if we cant then multiprocessing wont work
    MatchImages=copy.deepcopy(PrepareMatchImages)


    #build dictionary to remove items from
    for Index, img in enumerate(MatchImages.ImagesInMem_to_Process):
        MatchImages.DuplicatesToCheck[img]=img
    if MatchImages.GetDuplicates==True:
        ScanIndex=0
        StartingLength_images=len(MatchImages.DuplicatesToCheck)
        DuplicatesFound=0
        while len(MatchImages.DuplicatesToCheck)>0:
            print("Image Set remaining:",len(MatchImages.DuplicatesToCheck),"/",len(MatchImages.ImagesInMem_to_Process))
            #get any image from set
            BaseImageKey=random.choice(list(MatchImages.DuplicatesToCheck.keys()))
            BaseImage=MatchImages.ImagesInMem_to_Process[BaseImageKey]
            for image in MatchImages.ImagesInMem_to_Process:
                ScanIndex=ScanIndex+1
                TestImage=MatchImages.ImagesInMem_to_Process[image]
                HistogramSimilarity=MatchImages_lib. CompareHistograms(BaseImage.Histogram,TestImage.Histogram)
                if HistogramSimilarity<MatchImages.HistogramSelfSimilarityThreshold:
                    if BaseImageKey!=image:
                        print("Duplicate found!!",BaseImageKey,image)
                        DuplicatesFound=DuplicatesFound+1
                        cv2.imwrite(MatchImages.OutputDuplicates  + str(ScanIndex)+ "_File1_"+ str(HistogramSimilarity)+".jpg",MatchImages.ImagesInMem_to_Process[BaseImageKey].ImageColour)
                        cv2.imwrite(MatchImages.OutputDuplicates + str(ScanIndex)+ "_File2_"+ str(HistogramSimilarity)+".jpg",MatchImages.ImagesInMem_to_Process[image].ImageColour)
                        #if tracer file exists we can also save link to dat file and record
                        if MatchImages.TraceExtractedImg_to_DatRecordObj is not None:
                                Savefile_json=MatchImages.OutputDuplicates + str(ScanIndex) +"_DatRecord.txt"
                                DictOutputDetails=dict()
                                DictOutputDetails["BASEIMAGE"]=MatchImages.TraceExtractedImg_to_DatRecordObj[image]
                                DictOutputDetails["TESTEDIMAGE"]=MatchImages.TraceExtractedImg_to_DatRecordObj[BaseImageKey]
                                with open(Savefile_json, 'w') as outfile:
                                    json.dump(DictOutputDetails, outfile)
                        del MatchImages.DuplicatesToCheck[image]
            del MatchImages.DuplicatesToCheck[BaseImageKey]
        print(DuplicatesFound,"/",StartingLength_images," Duplicates found and stored at",MatchImages.OutputDuplicates)
        MatchImages.Endtime= time.time()
        print("time taken (hrs):",round((MatchImages.Endtime- MatchImages.startTime)/60/60 ),2)
        exit()



    #create indexed dictionary of images so we can start combining lists of images
    MatchImages.ImagesInMem_Pairing=dict()
    for Index, img in enumerate(MatchImages.ImagesInMem_to_Process):
        ImgCol_InfoSheet=ImgCol_InfoSheet_Class()
        ImgCol_InfoSheet.FirstImage=img
        MatchImages.ImagesInMem_Pairing[Index]=([img],ImgCol_InfoSheet)

    #initialise metric matrices
    MatchImages.HM_data_MetricDistances = np.zeros((len(MatchImages.ImagesInMem_Pairing),len(MatchImages.ImagesInMem_Pairing)))
    MatchImages.HM_data_MetricDistances_auto = np.zeros((len(MatchImages.ImagesInMem_Pairing),len(MatchImages.ImagesInMem_Pairing)))
    #initialise all metric matrices
    for MetricsMatrix in MatchImages.Metrics_dict:
        MatchImages.Metrics_dict[MetricsMatrix]=np.zeros((len(MatchImages.ImagesInMem_Pairing),len(MatchImages.ImagesInMem_Pairing)))


    #get info about cores for setting up multiprocess
    #WARNING might give weird results if inside a VM or a executable converted python 
    PhysicalCores=psutil.cpu_count(logical=False)#number of physical cores
    HyperThreadedCores = int(os.environ['NUMBER_OF_PROCESSORS'])#don't use these simulated cores
    #conditional user options
    if MatchImages.HyperThreading==True:
        print("Hyperthreading cores will be used (User option)")
        #user wants to use virtual cores - this might not be compatible with all similarity metrics
        Cores_Available=HyperThreadedCores
    else:
        print("Physical cores only will be used (User option)")
        #user just wants physical cores - we still dont know how windows distributes cores so may be virtual anyway
        Cores_Available=PhysicalCores
    #final core count available
    CoresTouse=1
    #user may have restricted performance to overcome memory errors or to leave system capacity for other tasks
    if MatchImages.MemoryError_ReduceLoad[0]==True and Cores_Available>1:
        CoresTouse=min(Cores_Available,MatchImages.MemoryError_ReduceLoad[1])#if user has over-specified cores restrict to cores available
        print("THROTTLING BY USER - Memory protection: restricting cores to", CoresTouse, ", user option MemoryError_ReduceLoad")
    else:
        CoresTouse=Cores_Available
    #if no restriction by user , leave a core anyway
    processes=max(CoresTouse-1,1)#rule is thumb is to use number of logical cores minus 1, but always make sure this number >0. Its not a good idea to blast CPU at 100% as this can reduce performance as OS tries to balance the load
    
    #find how much memory single process uses (windows)
    Currentprocess = psutil.Process(os.getpid())
    SingleProcess_Memory=Currentprocess.memory_percent()
    SystemMemoryUsed=psutil.virtual_memory().percent
    FreeMemoryBuffer_pc=MatchImages.FreeMemoryBuffer_pc#arbitrary free memory to leave
    MaxPossibleProcesses=max(math.floor((100-FreeMemoryBuffer_pc-SystemMemoryUsed)/SingleProcess_Memory),0)#can't be lower than zero
    print(MaxPossibleProcesses,"parallel processes possible at system capacity (leaving",FreeMemoryBuffer_pc,"% memory free)")
    print("Each process will use ~ ",round(psutil.virtual_memory().total*SingleProcess_Memory/100000000000,1),"gb")#convert bytes to gb
    #cannot proceed if we can't use even one core
    if processes<1 or MaxPossibleProcesses<1:
        print(("Multiprocess Configuration error! Less than 1 process possible - memory or logic error"))
        raise Exception("Multiprocess Configuration error! Less than 1 process possible - memory or logic error")
    #check system has enough memory - if not restrict cores used
    if processes>MaxPossibleProcesses:
        print("WARNING!! possible memory overflow - restricting number of processes from",processes,"to",MaxPossibleProcesses)
        processes=MaxPossibleProcesses
    #user option for process boost
    if MatchImages.BeastMode==False:
        chunksize=processes*3
    else:
        print("WARNING! Beast mode active - this optimisation prohibits any timing feedback")
        chunksize=int(len(MatchImages.ImagesInMem_Pairing)/processes)
    #how many jobs do we build up to pass off to the multiprocess pool, in this case in theory each core gets 3 stacked tasks
    ProcessesPerCycle=processes*chunksize
    
    #experimental with optimisation for multiprocessing
    #currently multiprocesses have staggered finish due to allotment of jobs
    #in this manner we wont have a situation where the first thread has the bigger range of the factorial jobs
    #and all processes more or less have some workload - this can be done more systematically but this
    #gets us most the way there without fiddly code
    print("Optimising parallel process load balance")
    SacrificialDictionary=copy.deepcopy(MatchImages.ImagesInMem_Pairing)
    ImagesInMem_Pairing_ForThreading=dict()
    while len(SacrificialDictionary)>0:
        RandomItem=random.choice(list(SacrificialDictionary.keys()))
        ImagesInMem_Pairing_ForThreading[RandomItem]=MatchImages.ImagesInMem_Pairing[RandomItem]
        del SacrificialDictionary[RandomItem]
    
    print("[Multiprocess start]","Taskstack per core:",chunksize,"  Taskpool size:",ProcessesPerCycle,"  Physical cores used:",processes,"   Images:",len(MatchImages.ImagesInMem_Pairing))
    pool = multiprocessing.Pool(processes=processes)
    listJobs=[]
    CompletedProcesses=0
    #start timer and time metrics
    listTimings=[]
    listCounts=[]
    listAvgTime=[]
    ProcessOnly_start = time.perf_counter()
    t1_start = time.perf_counter()
    for Index, BaseImageList in enumerate(ImagesInMem_Pairing_ForThreading):
        listJobs.append((MatchImages,BaseImageList))
        if (Index%ProcessesPerCycle==0 and Index!=0) or Index==len(MatchImages.ImagesInMem_Pairing)-1:
            ReturnList=(pool.imap_unordered(MatchImages_lib.ProcessSimilarity,listJobs,chunksize=chunksize))
            #populate output metric comparison matrices
            for ReturnObjects in ReturnList:
                Rtrn_CurrentBaseImage=ReturnObjects["BASEIMAGE"]
                for returnItem in MatchImages.Metrics_dict:
                    if returnItem in ReturnObjects:
                        MatchImages.Metrics_dict[returnItem][Rtrn_CurrentBaseImage,:]=ReturnObjects[returnItem]
                    else:
                        print("No match for",returnItem)

            CompletedProcesses=CompletedProcesses+len(listJobs)
            #get timings
            listTimings.append(round(time.perf_counter()-t1_start,2))
            listCounts.append(len(listJobs))
            listAvgTime.append(round(listTimings[-1]/listCounts[-1],3))
            #start timer again
            t1_start = time.perf_counter()
            print("Jobs done:", CompletedProcesses,"/",len(MatchImages.ImagesInMem_Pairing))
            #clear list of jobs
            listJobs=[]
            try:
                if len(listTimings)>3:
                    Diffy=listTimings[-1]-listTimings[1]
                    Diffx=len(listTimings)-1
                    m=Diffy/Diffx
                    _C=listTimings[1]-(m*1)
                    #playing around with time estimation
                    TaskLots=(len(MatchImages.ImagesInMem_Pairing)/ProcessesPerCycle)
                    TimeEstimate_sum=[]
                    TimeEstimateLeft_sum=[]
                    TimeEstimate_sum.append(listTimings[0])#first one is always non uniform
                    CurrentPosition=round(Index/ProcessesPerCycle)
                    for counter in range (1,int(TaskLots)):
                        _Y=(m*counter)+_C
                        if counter<CurrentPosition:
                            TimeEstimate_sum.append(listTimings[counter])
                        if counter>=CurrentPosition:
                            TimeEstimate_sum.append(round(_Y,2))
                            TimeEstimateLeft_sum.append(round(_Y,2))
                    # if len(listTimings)<7:
                    #     print("(more samples needed) Estimated total time=",str(datetime.timedelta(seconds=sum(TimeEstimate_sum))))
                    #     print("(more samples needed) Estimated Time left=",str(datetime.timedelta(seconds=sum(TimeEstimateLeft_sum))))
                    # else:
                    #     print("Estimated total time=",str(datetime.timedelta(seconds=sum(TimeEstimate_sum))))
                    #     print("Estimated Time left=",str(datetime.timedelta(seconds=sum(TimeEstimateLeft_sum))))
                    #second time estimate
                    slope, intercept, r_value, p_value, std_err = stats.linregress(range(0,len(listTimings[1:-1])),listTimings[1:-1])
                    TimeEstimate_sum=[]
                    TimeEstimateLeft_sum=[]
                    TimeEstimate_sum.append(listTimings[0])#first one is always non uniform
                    for counter in range (1,int(TaskLots)):
                        _Y=(slope*counter)+intercept
                        if counter<CurrentPosition:
                            TimeEstimate_sum.append(listTimings[counter])
                        if counter>=CurrentPosition:
                            TimeEstimate_sum.append(round(_Y,2))
                            TimeEstimateLeft_sum.append(round(_Y,2))
                    if len(listTimings)<7:
                        print("(More time samples needed) Estimated total time=",str(datetime.timedelta(seconds=sum(TimeEstimate_sum))))
                        print("(More time samples needed) Estimated Time left=",str(datetime.timedelta(seconds=sum(TimeEstimateLeft_sum))))
                    else:
                        print("Estimated total time=",str(datetime.timedelta(seconds=sum(TimeEstimate_sum))))
                        print("Estimated Time left=",str(datetime.timedelta(seconds=sum(TimeEstimateLeft_sum))))
            except:
                print("Problem with time estimate code")

    print("Total process only time:",str(datetime.timedelta(seconds= time.perf_counter()-ProcessOnly_start)))

    #create diagonally symetrical matrix
    for BaseImageList in MatchImages.ImagesInMem_Pairing:
        for testImageList in MatchImages.ImagesInMem_Pairing:
            if testImageList<BaseImageList:
                for MatchMetric in MatchImages.Metrics_dict:
                    MatchImages.Metrics_dict[MatchMetric][BaseImageList,testImageList]=MatchImages.Metrics_dict[MatchMetric][testImageList,BaseImageList]
    #fix any bad numbers
    for BaseImageList in MatchImages.ImagesInMem_Pairing:
        for testImageList in MatchImages.ImagesInMem_Pairing:
            for MatchMetric in MatchImages.Metrics_dict:
                if math.isnan( MatchImages.Metrics_dict[MatchMetric][BaseImageList,testImageList]):
                    MatchImages.Metrics_dict[MatchMetric][BaseImageList,testImageList]=MatchImages.DummyMinValue
                    print("Bad value found, ",MatchMetric)

    #normalize
    for MatchMetric in MatchImages.Metrics_dict:
        MatchImages.Metrics_dict[MatchMetric]=normalize_2d(np.where(MatchImages.Metrics_dict[MatchMetric]==MatchImages.DummyMinValue, MatchImages.Metrics_dict[MatchMetric].max()+1, MatchImages.Metrics_dict[MatchMetric]))


    for BaseImageList in MatchImages.ImagesInMem_Pairing:
        for TestImageList in MatchImages.ImagesInMem_Pairing:
            if TestImageList<BaseImageList:
                #data is diagonally symmetrical
                continue
            #create total of all metrics
            BuildUpTotals=[]
            for MatchMetric in MatchImages.Metrics_dict:
                if math.isnan(MatchImages.Metrics_dict[MatchMetric][BaseImageList,TestImageList]):
                    BuildUpTotals.append(MatchImages.Metrics_dict[MatchMetric][BaseImageList,TestImageList])
                else:
                    BuildUpTotals.append(MatchImages.Metrics_dict[MatchMetric][BaseImageList,TestImageList])
            SquaredSum=0
            for Total in BuildUpTotals:
                SquaredSum=SquaredSum+Total**2
            MatchImages.HM_data_MetricDistances[TestImageList,BaseImageList]=MatchImages.HM_data_MetricDistances[TestImageList,BaseImageList]+math.sqrt(SquaredSum)
             #mirror data for visualisation
            MatchImages.HM_data_MetricDistances[BaseImageList,TestImageList]=MatchImages.HM_data_MetricDistances[TestImageList,BaseImageList]

    #normalise final data
    MatchImages.HM_data_MetricDistances=normalize_2d(MatchImages.HM_data_MetricDistances)


    #save data out as pickle/data

    
    MatchImages_lib.PrintResults(MatchImages,PlotAndSave_2datas,PlotAndSave)

    #sequential matching
    MatchImages_lib.SequentialMatchingPerImage(copy.deepcopy(MatchImages),PlotAndSave_2datas,PlotAndSave)

    #pairwise matching
    MatchImages_lib.PairWise_Matching(copy.deepcopy(MatchImages),PlotAndSave_2datas,PlotAndSave,ImgCol_InfoSheet_Class)

    



class CheckImages_Class():
    def __init__(self):
        self.AllHisto_results=[]
        self.All_FM_results=[]
        self.All_EigenDotProd_result=[]
        self.MatchingImgLists=[]
        self.BestMatch_Histo=99999999
        self.BestMatch_Histo_listIndex=None
        self.BestMatch_FeatureMatch=99999999
        self.BestMatch_FeatureMatch_listIndex=None
        


class ImgCol_InfoSheet_Class():
    def __init__(self):
        self.InUse=True
        self.Cycles=0
        self.AllImgs_Histo_Std=0
        self.AllImgs_Hist_mean=0
        self.AllImgs_FM_std=0
        self.AllImgs_FM_mean=0
        self.FirstImage=None
        self.StatsOfList=[]



if __name__ == "__main__":
    #entry point
    #try:
    
    main()
    #except Exception as e:
    #    ##note: cleaning up after exception should be to set os.chdir(anything else) or it will lock the folder
    #    print(e)
    #    # printing stack trace
    #    print("Press any key to continue")
    #    os.system('pause')