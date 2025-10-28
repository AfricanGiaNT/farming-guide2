import { configureStore, combineReducers } from '@reduxjs/toolkit'
import { persistStore, persistReducer, FLUSH, REHYDRATE, PAUSE, PERSIST, PURGE, REGISTER } from 'redux-persist'
import userReducer from './slices/userSlice'
import weatherReducer from './slices/weatherSlice'
import cropReducer from './slices/cropSlice'
import knowledgeReducer from './slices/knowledgeSlice'
import { createExpiringStorage, persistTransform } from '../utils/persistentStorage'

// Create custom storage with 12-hour expiration
const expiringStorage = createExpiringStorage()

// Configure persistence
const persistConfig = {
  key: 'root',
  storage: expiringStorage,
  whitelist: ['user', 'weather', 'crop', 'knowledge'], // Only persist these slices
  transforms: [persistTransform],
}

// Combine reducers
const rootReducer = combineReducers({
  user: userReducer,
  weather: weatherReducer,
  crop: cropReducer,
  knowledge: knowledgeReducer,
})

// Create persisted reducer
const persistedReducer = persistReducer(persistConfig, rootReducer)

// Configure store
export const store = configureStore({
  reducer: persistedReducer,
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: {
        ignoredActions: [FLUSH, REHYDRATE, PAUSE, PERSIST, PURGE, REGISTER],
      },
    }),
})

// Create persistor
export const persistor = persistStore(store)

export type RootState = ReturnType<typeof store.getState>
export type AppDispatch = typeof store.dispatch