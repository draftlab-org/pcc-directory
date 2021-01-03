<script>
import { readable, get } from 'svelte/store';

import { maps_indicators } from '../store.js';

import IndicatorCard from './IndicatorCard.svelte'

</script>

<ul class="cards">
    {#if $maps_indicators.countries != undefined}
        <IndicatorCard title="Countries" reader="countries" number={$maps_indicators.countries} />
    {/if}
    {#if $maps_indicators.projects != undefined}
        <IndicatorCard title="Projects" reader="projects" number={$maps_indicators.projects} />
    {/if}
</ul>
