import React, { useState, useEffect } from 'react';
import { StyleSheet, View, Button } from 'react-native';
import MapView, { Marker, Polyline } from 'react-native-maps';
import polyline from '@mapbox/polyline';

export default function TabTwoScreen() {
  const [routeCoordinates, setRouteCoordinates] = useState<{ latitude: number; longitude: number }[]>([]);
  const [originCoords, setOriginCoords] = useState<{ latitude: number; longitude: number } | null>(null);
  const [destinationCoords, setDestinationCoords] = useState<{ latitude: number; longitude: number } | null>(null);
  const [mode, setMode] = useState<'driving' | 'walking' | 'transit'>('driving'); // Default mode is driving

  const apiKey = 'AIzaSyCPtlKAn2duBP35t1xGaB2UCYU7AvD4p-o'; // Replace with your Google Maps API key
  const origin = "5610 Kullahun Drive"; // Address
  const destination = "UBC Bus Loop"; // Address
  const bcPlaceCoords = { latitude: 49.2768, longitude: -123.1112 }; // BC Place coordinates

  useEffect(() => {
    fetchCoordinates(); // Get lat/lng for origin and destination
  }, []);

  useEffect(() => {
    if (originCoords && destinationCoords) {
      fetchRoute(); // Fetch the route once coordinates are available
    }
  }, [originCoords, destinationCoords, mode]);

  const fetchCoordinates = async () => {
    try {
      // Fetch coordinates for the origin
      const originResponse = await fetch(
        `https://maps.googleapis.com/maps/api/geocode/json?address=${encodeURIComponent(origin)}&key=${apiKey}`
      );
      const originData = await originResponse.json();
      if (originData.results.length) {
        const { lat, lng } = originData.results[0].geometry.location;
        setOriginCoords({ latitude: lat, longitude: lng });
      }

      // Fetch coordinates for the destination
      const destinationResponse = await fetch(
        `https://maps.googleapis.com/maps/api/geocode/json?address=${encodeURIComponent(destination)}&key=${apiKey}`
      );
      const destinationData = await destinationResponse.json();
      if (destinationData.results.length) {
        const { lat, lng } = destinationData.results[0].geometry.location;
        setDestinationCoords({ latitude: lat, longitude: lng });
      }
    } catch (error) {
      console.error('Error fetching coordinates:', error);
    }
  };

  const fetchRoute = async () => {
    try {
      if (!originCoords || !destinationCoords) return; // Safeguard against null origin or destination

      const originStr = `${originCoords.latitude},${originCoords.longitude}`;
      const destinationStr = `${destinationCoords.latitude},${destinationCoords.longitude}`;
      const url = `https://maps.googleapis.com/maps/api/directions/json?origin=${originStr}&destination=${destinationStr}&mode=${mode}&key=${apiKey}`;

      const response = await fetch(url);
      const data = await response.json();

      if (data.routes.length) {
        // Decode the polyline from the API response
        const points: [number, number][] = polyline.decode(data.routes[0].overview_polyline.points);
        const coordinates = points.map(([lat, lng]: [number, number]) => ({
          latitude: lat,
          longitude: lng,
        }));
        setRouteCoordinates(coordinates);
      }
    } catch (error) {
      console.error('Error fetching route:', error);
    }
  };

  return (
    <View style={styles.container}>
      {/* Map */}
      <MapView
        style={styles.map}
        initialRegion={{
          latitude: originCoords ? originCoords.latitude : 49.2676,
          longitude: originCoords ? originCoords.longitude : -123.2522,
          latitudeDelta: 0.05,
          longitudeDelta: 0.05,
        }}
      >
        {/* Origin Marker */}
        {originCoords && (
          <Marker coordinate={originCoords} title="Origin" description={origin} />
        )}

        {/* Destination Marker */}
        {destinationCoords && (
          <Marker coordinate={destinationCoords} title="Destination" description={destination} />
        )}

        {/* BC Place Marker */}
        <Marker coordinate={bcPlaceCoords} title="BC Place" description="Stadium in Vancouver" />

        {/* Route Polyline */}
        {routeCoordinates.length > 0 && (
          <Polyline coordinates={routeCoordinates} strokeWidth={4} strokeColor="blue" />
        )}
      </MapView>

      {/* Mode Buttons */}
      <View style={styles.buttons}>
        <Button title="Driving" onPress={() => setMode('driving')} />
        <Button title="Walking" onPress={() => setMode('walking')} />
        <Button title="Transit" onPress={() => setMode('transit')} />
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  map: {
    width: '100%',
    height: '80%',
  },
  buttons: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    padding: 10,
  },
});
