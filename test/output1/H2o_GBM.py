#!/usr/bin/env python
# coding: utf-8

# H2O and GBM modules
# 

# In[1]:


import h2o
h2o.init()


# In[2]:


from h2o.estimators.gbm import H2OGradientBoostingEstimator


# In[3]:


#airlines = h2o.import_file("https://s3.amazonaws.com/h2o-public-test-data/smalldata/airlines/allyears2k_headers.zip")
airlines = h2o.import_file("/Users/dt216661/Documents/MyH2o/H2O/data/allyears2k_headers.zip")


# In[4]:


airlines.head(4)


# In[5]:


airlines['Year'] = airlines['Year'].asfactor()
airlines['Month'] = airlines['Month'].asfactor()
airlines['DayOfWeek'] = airlines['DayOfWeek'].asfactor()
airlines['Cancelled'] = airlines['Cancelled'].asfactor()
airlines['FlightNum'] = airlines['FlightNum'].asfactor()


# In[6]:


predictors = ['Origin','Dest','Year','UniqueCarrier','DayOfWeek','Month','Distance','FlightNum'] 
response = 'IsDepDelayed'


# In[7]:


train, valid = airlines.split_frame(ratios = [.8], seed = 1234)


# In[8]:


bin_num = [8, 16, 32, 64, 128, 256, 512, 1024, 2048, 4096]
label = "8", "16", "32", "64", "128", "256", "512", "1024", "2016", "4096" 


# In[9]:


for key, num in enumerate(bin_num):
    print('bin'+ str(key) + ' with number: '+ str(num))
    airlines_gbm = H2OGradientBoostingEstimator(nbins_cats = num, seed =1234)
    airlines_gbm.train(x = predictors, y = response, training_frame = train, validation_frame = valid)


# In[10]:


print(label[key], "training socre", airlines_gbm.auc(train = True))
print(label[key], "validation socre", airlines_gbm.auc(valid = True))

