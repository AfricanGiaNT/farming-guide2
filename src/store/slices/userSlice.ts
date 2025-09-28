import { createSlice, PayloadAction } from '@reduxjs/toolkit'

interface UserLocation {
  lat: number
  lon: number
  accuracy: number | null
}

interface UserProfile {
  id?: string
  name?: string
  farmSize?: number
  primaryCrops?: string[]
  location?: UserLocation
  preferences?: {
    language: 'en' | 'ny' // English or Chichewa
    units: 'metric' | 'imperial'
    notifications: boolean
  }
}

interface UserState {
  profile: UserProfile
  isAuthenticated: boolean
  location: UserLocation | null
  onboardingCompleted: boolean
}

const initialState: UserState = {
  profile: {
    preferences: {
      language: 'en',
      units: 'metric',
      notifications: true,
    },
  },
  isAuthenticated: false,
  location: null,
  onboardingCompleted: false,
}

const userSlice = createSlice({
  name: 'user',
  initialState,
  reducers: {
    setUserLocation: (state, action: PayloadAction<UserLocation>) => {
      state.location = action.payload
      if (state.profile) {
        state.profile.location = action.payload
      }
    },
    updateUserProfile: (state, action: PayloadAction<Partial<UserProfile>>) => {
      state.profile = { ...state.profile, ...action.payload }
    },
    setAuthenticated: (state, action: PayloadAction<boolean>) => {
      state.isAuthenticated = action.payload
    },
    completeOnboarding: (state) => {
      state.onboardingCompleted = true
    },
    updatePreferences: (state, action: PayloadAction<Partial<UserProfile['preferences']>>) => {
      if (state.profile.preferences) {
        state.profile.preferences = { ...state.profile.preferences, ...action.payload }
      }
    },
  },
})

export const {
  setUserLocation,
  updateUserProfile,
  setAuthenticated,
  completeOnboarding,
  updatePreferences,
} = userSlice.actions

export default userSlice.reducer