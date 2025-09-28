import { configureStore } from '@reduxjs/toolkit'
import userReducer from './slices/userSlice'
import weatherReducer from './slices/weatherSlice'
import cropReducer from './slices/cropSlice'
import knowledgeReducer from './slices/knowledgeSlice'

export const store = configureStore({
  reducer: {
    user: userReducer,
    weather: weatherReducer,
    crop: cropReducer,
    knowledge: knowledgeReducer,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: {
        ignoredActions: ['persist/PERSIST'],
      },
    }),
})

export type RootState = ReturnType<typeof store.getState>
export type AppDispatch = typeof store.dispatch