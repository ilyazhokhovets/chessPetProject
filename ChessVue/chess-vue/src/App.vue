<template>
 <div id="app">

  <router-view/>

    </div>
</template>

<style>

</style>
<script>

import Socket from "@/components/Socket";
import Settings from "@/components/Settings";
export default {
  components: {Socket, Settings}
}
</script>