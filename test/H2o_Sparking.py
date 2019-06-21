#!/usr/bin/env python
# coding: utf-8

# In[ ]:


sc.version


# In[1]:


sc.addPyFile("/Users/dt216661/sparkling-water-2.4.5/py/build/dist/h2o_pysparkling_2.4-2.4.5.zip")


# In[2]:


import h2o
from pysparkling import H2OContext
h2o.__version__
hc = H2OContext.getOrCreate(spark)
print(hc)


# # 1.Start H2O cluster inside the Spark environment

# In[4]:


from pysparkling import *
hc = H2OContext.getOrCreate(spark)


# # 2. Parse the data using H2O and convert them to Spark Frame

# In[6]:


import h2o
frame = h2o.import_file("https://raw.githubusercontent.com/h2oai/sparkling-water/master/examples/smalldata/prostate/prostate.csv")
spark_frame = hc.as_spark_frame(frame)


# In[7]:


spark_frame.show(4)


# In[8]:


spark_frame.describe()


# # 3. Train the model

# In[10]:


from pysparkling.ml import H2OXGBoost
estimator = H2OXGBoost(predictionCol="AGE")
model = estimator.fit(spark_frame)


# # 4. Run Predictions

# In[12]:


predictions = model.transform(spark_frame)


# In[13]:


predictions.show(4)


# In[14]:




