import { defineStore } from 'pinia'
import { ref } from 'vue'

export interface Drone {
  id: string
  name: string
  model: string
  serialNumber: string
  status: 'available' | 'flying' | 'maintenance' | 'retired'
  position: {
    lat: number
    lng: number
    altitude: number
  }
  battery: number
  signal: number
  mission?: string
}

export interface Airspace {
  id: string
  name: string
  type: 'flyable' | 'restricted' | 'prohibited'
  coordinates: number[][]
  status: 'available' | 'occupied' | 'unavailable'
  altitude: {
    min: number
    max: number
  }
}

export const useMapStore = defineStore('map', () => {
  const drones = ref<Drone[]>([])
  const airspaces = ref<Airspace[]>([])
  const selectedDrone = ref<Drone | null>(null)
  const mapCenter = ref<[number, number]>([39.9042, 116.4074]) // 北京
  const mapZoom = ref(10)

  const addDrone = (drone: Drone) => {
    drones.value.push(drone)
  }

  const updateDronePosition = (id: string, position: Drone['position']) => {
    const drone = drones.value.find(d => d.id === id)
    if (drone) {
      drone.position = position
    }
  }

  const selectDrone = (drone: Drone | null) => {
    selectedDrone.value = drone
  }

  const addAirspace = (airspace: Airspace) => {
    airspaces.value.push(airspace)
  }

  const updateAirspaceStatus = (id: string, status: Airspace['status']) => {
    const airspace = airspaces.value.find(a => a.id === id)
    if (airspace) {
      airspace.status = status
    }
  }

  return {
    drones,
    airspaces,
    selectedDrone,
    mapCenter,
    mapZoom,
    addDrone,
    updateDronePosition,
    selectDrone,
    addAirspace,
    updateAirspaceStatus
  }
})
