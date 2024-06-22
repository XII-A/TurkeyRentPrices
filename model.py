# Description: predict the house rent price, based of its features using deep learning
# import the depndencies

# data analysis and wrangling
import pandas as pd
import numpy as np
import random as rnd

# visualization
import seaborn as sns
import matplotlib.pyplot as plt
%matplotlib inline

# scaling and train test split
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import GridSearchCV

# creating a model
from keras.models import Sequential
from keras.layers import Dense, Activation
from keras.optimizers import Adam
from keras.callbacks import EarlyStopping
from keras.callbacks import Callback
from keras.layers import Dropout
from keras import regularizers
from keras.layers import BatchNormalization


# evaluation on test data
from sklearn.metrics import mean_squared_error,mean_absolute_error,explained_variance_score
from sklearn.metrics import classification_report,confusion_matrix

df = pd.read_csv('finalDataModelCityMean.csv', low_memory=False, index_col=False)
df.dropna(inplace=True)
pd.set_option('display.float_format', lambda x: '%.5f' % x)
pd.options.display.max_columns = 500
pd.options.display.max_rows = 10000

def get_z_score(value,mean,std):
    return (value-mean)/std
# logging the fiyat
df['log_fiyat'] = np.log1p(df['fiyat'])
df.drop(['fiyat'], axis=1, inplace=True)
# removing outliers
df['z_score_fiyat'] = df['log_fiyat'].apply(lambda x: get_z_score(x,df['log_fiyat'].mean(),df['log_fiyat'].std()))
filtered_data = df[df['z_score_fiyat'] < 3]
df = filtered_data
df.drop(['z_score_fiyat'], axis=1, inplace=True)

df['mean_by_district'] = df.groupby('district')['log_fiyat'].transform('mean')
df['mean_by_neighborhood'] = df.groupby('neighborhood')['log_fiyat'].transform('mean')
df['mean_by_city'] = df.groupby('city')['log_fiyat'].transform('mean')

df.drop(["city","district","neighborhood"], axis=1, inplace=True)

# combine bedroom and living room

df['rooms'] = df['living_rooms'] + df['bedrooms']
df.drop(['living_rooms', 'bedrooms'], axis=1, inplace=True)


X = df.drop(['log_fiyat'],axis=1)
y = df['log_fiyat']
X_train, X_test, y_train, y_test = train_test_split(X,y,test_size=0.3,random_state=101)


scaler = MinMaxScaler()

# fit and transfrom
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)

# everything has been scaled between 1 and 0
print('Max: ',X_train.max())
print('Min: ', X_train.min())


model = Sequential()

# input layer
model.add(Dense(64, activation='relu', input_shape=(34,)))

# hidden layers
model.add(Dense(64, activation='relu', kernel_regularizer=regularizers.l2(0.01)))
model.add(BatchNormalization())
model.add(Dropout(0.1))

model.add(Dense(64, activation='relu', kernel_regularizer=regularizers.l2(0.01)))
model.add(BatchNormalization())
model.add(Dropout(0.1))

model.add(Dense(64, activation='relu', kernel_regularizer=regularizers.l2(0.01)))



# output layer
model.add(Dense(1))

model.compile(optimizer=Adam(learning_rate=0.001),loss='mse', metrics = 'mse')


early_stopping = EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True)

model.fit(x=X_train,y=y_train.values,
          validation_data=(X_test,y_test.values),
          batch_size=128,epochs=400,
          callbacks = [early_stopping]
          )

losses = pd.DataFrame(model.history.history)

plt.figure(figsize=(15,5))
sns.lineplot(data=losses,lw=3)
plt.xlabel('Epochs')
plt.ylabel('')
plt.title('Training Loss per Epoch')
sns.despine()


# predictions on the test set
predictions = model.predict(X_test)

print('MAE: ',mean_absolute_error(y_test,predictions))
print('MSE: ',mean_squared_error(y_test,predictions))
print('RMSE: ',np.sqrt(mean_squared_error(y_test,predictions)))
print('Variance Regression Score: ',explained_variance_score(y_test,predictions))

print('\n\nDescriptive Statistics:\n',df['log_fiyat'].describe())


f, axes = plt.subplots(1, 2,figsize=(15,5))

# Our model predictions
plt.scatter(y_test,predictions)

# Perfect predictions
plt.plot(y_test,y_test,'r')

errors = y_test.values.reshape(7062, 1) - predictions
sns.distplot(errors, ax=axes[0])

sns.despine(left=True, bottom=True)
axes[0].set(xlabel='Error', ylabel='', title='Error Histogram')
axes[1].set(xlabel='Test True Y', ylabel='Model Predictions', title='Model Predictions vs Perfect Fit')

test_loss = model.evaluate(X_test, y_test.values)
print(f'Test Loss: {test_loss}')
