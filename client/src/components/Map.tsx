/**
 * Shared Google Maps frontend integration.
 * The loader is intentionally singleton/idempotent because map views can mount
 * and unmount when users switch between terrain and satellite modes.
 */
/// <reference types="@types/google.maps" />

import { useEffect, useRef } from "react";
import { usePersistFn } from "@/hooks/usePersistFn";
import { cn } from "@/lib/utils";

declare global {
  interface Window {
    google?: typeof google;
  }
}

const API_KEY = import.meta.env.VITE_GOOGLE_MAPS_API_KEY;
const MAPS_SCRIPT_ATTRIBUTE = "data-manus-google-maps";

let mapsScriptPromise: Promise<void> | null = null;

function loadMapScript(): Promise<void> {
  if (typeof window === "undefined") return Promise.resolve();
  if (window.google?.maps) return Promise.resolve();
  if (mapsScriptPromise) return mapsScriptPromise;

  const existingScript = document.querySelector<HTMLScriptElement>(`script[${MAPS_SCRIPT_ATTRIBUTE}]`);
  if (existingScript) {
    mapsScriptPromise = new Promise<void>((resolve, reject) => {
      existingScript.addEventListener("load", () => resolve(), { once: true });
      existingScript.addEventListener("error", () => reject(new Error("Failed to load Google Maps")), { once: true });
    });
    return mapsScriptPromise;
  }

  mapsScriptPromise = new Promise<void>((resolve, reject) => {
    const script = document.createElement("script");
    script.setAttribute(MAPS_SCRIPT_ATTRIBUTE, "true");
    if (!API_KEY) {
      reject(new Error("VITE_GOOGLE_MAPS_API_KEY is not configured"));
      return;
    }
    script.src = `https://maps.googleapis.com/maps/api/js?key=${API_KEY}&v=weekly&libraries=marker,places,geocoding,geometry`;
    script.async = true;
    script.crossOrigin = "anonymous";
    script.onload = () => resolve();
    script.onerror = () => {
      mapsScriptPromise = null;
      reject(new Error("Failed to load Google Maps script"));
    };
    document.head.appendChild(script);
  });

  return mapsScriptPromise;
}

interface MapViewProps {
  className?: string;
  initialCenter?: google.maps.LatLngLiteral;
  initialZoom?: number;
  onMapReady?: (map: google.maps.Map) => void;
}

export function MapView({
  className,
  initialCenter = { lat: 37.7749, lng: -122.4194 },
  initialZoom = 12,
  onMapReady,
}: MapViewProps) {
  const mapContainer = useRef<HTMLDivElement>(null);
  const map = useRef<google.maps.Map | null>(null);
  const hasInitialized = useRef(false);

  const init = usePersistFn(async () => {
    if (hasInitialized.current || !mapContainer.current) return;
    hasInitialized.current = true;

    try {
      await loadMapScript();
      if (!mapContainer.current || !window.google?.maps) return;
      map.current = new window.google.maps.Map(mapContainer.current, {
        zoom: initialZoom,
        center: initialCenter,
        mapTypeControl: true,
        fullscreenControl: true,
        zoomControl: true,
        streetViewControl: true,
        mapId: "DEMO_MAP_ID",
      });
      onMapReady?.(map.current);
    } catch (error) {
      hasInitialized.current = false;
      console.error("[Maps] Failed to initialize Google Maps", error);
    }
  });

  useEffect(() => {
    void init();
  }, [init]);

  return <div ref={mapContainer} className={cn("h-[500px] w-full", className)} />;
}
