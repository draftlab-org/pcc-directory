import Cards from './components/Cards.svelte';
import CardsIndicators from './components/CardsIndicators.svelte';
import Popup from './components/Popup.svelte';
import { features, maps_indicators } from './store.js';

/**
 * Instantiate the Svelte container for organization and individual cards below the map.
 */
export const generateCards = () => {
  new Cards({
    target: document.getElementById('visibles')
  });
};

/**
 * 
 * @param {mapboxgl.Map} map The main map instance.
 * @param {Array} layers The layers to search for features in the current map view.
 */
export const updateStore = (map, layers) => {
  let visibleFeatures = map.queryRenderedFeatures({layers: layers});
  if (visibleFeatures) {
    const visibleFeaturesStatus = document.querySelector('#visible-features');
    visibleFeaturesStatus.innerText = (visibleFeatures.length == 1) ? `showing ${visibleFeatures.length} organization or individual` : `showing ${visibleFeatures.length} organizations and/or individuals`;
    features.set(visibleFeatures);
  }
};

export const generatePopupHtml = (f) => {
  const popup = document.createElement('div');
  new Popup({
    target: popup,
    props: {
      feature: f
    }
  });
  return popup.innerHTML;
};


/**
 * Instantiate the Svelte container for indicators cards above the map.
 */
export const generateMapsIdicatorsCards = () => {
  new CardsIndicators({
    target: document.getElementById('maps-indicators')
  });
};

export const setMapsIdicators = (idicators) => {
  maps_indicators.set(idicators);
}