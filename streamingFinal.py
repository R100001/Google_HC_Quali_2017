"""
* Η σκέψη είναι να υπολογίστουν όλα τα score για τα βίντεο άμα τοποθετούνταν
* σε κάποια cache και να επιλέγεται καθέ φορά το καλύτερο.
"""

import time

def binarySortAndDictUpdate(cache, videoIndex, videoDict):
    video = cache.pop(videoIndex)
    if video[1][0] <= 0:
        videoDict.pop(video[0])
        for pos, video in enumerate(cache[videoIndex:]):
            videoDict.update({video[0]:pos+videoIndex})
        return
    start = 0
    end = videoIndex - 1
    if end == -1:
        cache.insert(0, video)
        videoDict.update({video[0]:0})
        return
    while start <= end:
        middle = (start + end) // 2
        if video[1][0] == cache[middle][1][0]:
            break
        elif video[1][0] < cache[middle][1][0]:
            end = middle - 1
        else:
            start = middle + 1
    if video[1][0] <= cache[middle][1][0]:
        cache.insert(middle, video)
        for pos, video in enumerate(cache[middle:videoIndex+1]):
            videoDict.update({video[0]:pos+middle})
    else:
        cache.insert(middle+1, video)
        for pos, video in enumerate(cache[middle+1:videoIndex+1]):
            videoDict.update({video[0]:pos+middle+1})

def videoScore(video):
    return video[1][0]

def lastVideoOnEveryList(aList):
    try:
        return videoScore(aList[-1])
    except IndexError: #άμα είναι κενή η λίστα
        return 0

filename = int(input("0:pdf.in(105Bytes), 1:me_at_the_zoo(1.37KB), 2:videos_worth_spreading(1.13MB),\
3:trending_today(1.38MB), 4:kittens(5.42MB): "))

if filename == 1:
    filename = "me_at_the_zoo.in"
if filename == 2:
    filename = "videos_worth_spreading.in"
elif filename == 3:
    filename = "trending_today.in"
elif filename == 4:
    filename = "kittens.in.txt"
else:
    filename = "pdf.in"

x = time.time()

with open(filename, 'r') as infile:
    
    nVideos, nEndpoints, nRequests, nCaches, cacheSize = map(int, infile.readline().split())
    
    *videoSizes, = map(int, infile.readline().split())
    
    cachesInfo = [[dict(), dict(), dict()] for i in range(nCaches)] # για κάθε cache στο πρώτο λεξικό έχουμε ζεύγη endpoint
                                                                    # με τον χρόνο που κερδίζουμε, στο δεύτερο τα βίντεο
                                                                    # με τα σκορ που θα είχαν άμα έμπαιναν σε αυτήν την cache
                                                                    # και το μέγεθος τους και στο τρίτο το κάθε score που
                                                                    # που έχει η cache για κάθε request ενός βίντεο από ενα
                                                                    # endpoint
    endsConnedCaches = [[] for i in range(nEndpoints)] # ποιες caches είναι συνδεδεμένες σε κάθε endpoint
    for endpoint in range(nEndpoints):
        datacenterLatency, connectedCaches = map(int, infile.readline().split())
        
        for connectedCache in range(connectedCaches):
            cacheNumber, cacheLatency = map(int, infile.readline().split())
            
            endsConnedCaches[endpoint].append(cacheNumber)
            cachesInfo[cacheNumber][0].update({endpoint:datacenterLatency - cacheLatency})
            
    
    totalRequests = 0
    endsReqedVideo = [dict() for i in range(nVideos)] # ποια endpoints έχουν κάνει request το κάθε βίντεο
    
    for request in range(nRequests):
        video, endpoint, requests = map(int, infile.readline().split())
        endsReqedVideo[video].update({endpoint:requests})
        totalRequests += requests
        
        for cacheNumber in endsConnedCaches[endpoint]:
            latencyDiff = cachesInfo[cacheNumber][0][endpoint]
            score = (latencyDiff * requests) / videoSizes[video]
            
            if video not in cachesInfo[cacheNumber][1]:
                cachesInfo[cacheNumber][1].update({video:
                                                    [score, videoSizes[video]]})
            else:
                cachesInfo[cacheNumber][1][video][0] += score
            
            cachesInfo[cacheNumber][2].update({(endpoint,video):[score,score]})

cachesList = [[] for cache in range(nCaches)] # δημιουργούνται λίστες για να έχουμε ταξινόμηση και πιο γρήγορη εύρεση
                                              # του βίντεο με το καλύτερο σκορ στις λίστες
for cache in range(nCaches):
    cachesList[cache] = sorted(list(cachesInfo[cache][1].items()), key=videoScore)

videoScores = [dict(cachesInfo[cache][2]) for cache in range(nCaches)]
 # αυτά τα λεξικά δημιουργούνται γιατί όταν ένα βίντεο μπαίνει σε μία cache
 # στις άλλες πρέπει να αφαιρείται το σκορ που έχει ήδη προστεθεί από αυτήν
 # την τοποθέτηση (το εξηγώ πως παρακάτω)
    
videosIndexInCacheList = [] # αυτή η λίστα με λεξικά χρησιμοποιείται για να μην κάνουμε αναζήτηση σε κάθε cache
                            # που βρίσκεται το κάθε βίντεο
for cache in cachesList:
    videoDict = dict()
    for position, video in enumerate(cache):
        videoDict.update({video[0]:position})
    videosIndexInCacheList.append(videoDict)
    
videosInCaches = [[] for i in range(nCaches)] # λίστα για την δημιουργία του output.. δε βοηθάει κάπου στον αλγόριθμο
score = 0

cacheSizes = [0 for i in range(nCaches)] # λίστα που κρατάει τα μεγέθη όλων των βίντεο για να μην ξεπεραστεί το όριο
while True:
    listWithMaxScore = max(cachesList, key=lastVideoOnEveryList) # εύρεση της cache που έχει το βίντεο με το
                                                                 # μεγαλύτερο σκορ
    cache = cachesList.index(listWithMaxScore)
    try:
        video = listWithMaxScore.pop(-1)
    except IndexError: # άμα συμβεί αυτό τότε όλες οι λίστες είναι κενές και σημαίνει ότι ελέγξαμε τα πάντα
        break
    videosIndexInCacheList[cache].pop(video[0])
    if video[1][1] + cacheSizes[cache] <= cacheSize: #άμα το βίντεο χωράει στην cache
        cacheSizes[cache] += video[1][1]
        videosInCaches[cache].append(video)
        score += video[1][0] * video[1][1]
        for endpoint in cachesInfo[cache][0]:
            for connectedCache in endsConnedCaches[endpoint]: # σε αυτές τις δυο for ελέγχονται όλες οι cache
                                                              # που επιρεάζονται τα σκορ τους από την τοποθέτηση
                                                              # του βίντεο
                try:
                    videoIndex = videosIndexInCacheList[connectedCache][video[0]]
                    
                    if videoScores[connectedCache][(endpoint,video[0])][1] == 0: # άμα το σκορ δεν επιρεάζεται από αυτό το βίντεο
                        continue                                                 # σε αυτήν την cache
                    
                    if cachesInfo[cache][0][endpoint] >= cachesInfo[connectedCache][0][endpoint]:
                        # αν η cache που τοποθετήθηκε το βίντεο έχει μικρότερη καθηστέρηση από τις άλλες συνδεδεμένες με το endpoint
                        # τότε αφαιρείται όλο το score που δίνει αυτό το endpoint στις άλλες cache με αυτό το βίντεο
                        
                        cachesList[connectedCache][videoIndex][1][0] -= videoScores[connectedCache][(endpoint,video[0])][1]
                        
                        videoScores[connectedCache][(endpoint,video[0])][1] = 0
                        
                        binarySortAndDictUpdate(cachesList[connectedCache], videoIndex,
                                                videosIndexInCacheList[connectedCache])
                        
                    elif videoScores[connectedCache][(endpoint,video[0])][0] \
                                - cachesInfo[cache][0][endpoint] * endsReqedVideo[video[0]][endpoint] \
                                < videoScores[connectedCache][(endpoint,video[0])][1]:
                        # αν όμως δεν έχει μικρότερη καθηστέρηση και το score που θα αφαιρεθεί είναι περισσότερο από κάθε άλλη φορά
                        # τότε το καινούριο score είναι αυτό που διαμορφώνεται τώρα

                        cachesList[connectedCache][videoIndex][1][0] -= videoScores[connectedCache][(endpoint,video[0])][1] \
                                    - ( videoScores[connectedCache][(endpoint,video[0])][0] 
                                    - cachesInfo[cache][0][endpoint] * endsReqedVideo[video[0]][endpoint] )
                        
                        videoScores[connectedCache][(endpoint,video[0])][1] = videoScores[connectedCache][(endpoint,video[0])][0] \
                                - cachesInfo[cache][0][endpoint] * endsReqedVideo[video[0]][endpoint]
                        
                        binarySortAndDictUpdate(cachesList[connectedCache], videoIndex,
                                                videosIndexInCacheList[connectedCache])
                        
                except KeyError: # άμα το βίντεο δεν υπάρχει στην cache
                    pass

print((score/totalRequests)*1000)
            
print(time.time()-x)