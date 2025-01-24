<script setup lang="ts">
import { RouterView } from 'vue-router'
</script>

<template>
  <header></header>
  <div class="locale-changer">
    <select v-model="$i18n.locale">
      <option v-for="locale in $i18n.availableLocales" :key="`locale-${locale}`" :value="locale">
        {{ locale }}
      </option>
    </select>
  </div>
  <main>
    <RouterView />
  </main>
</template>
