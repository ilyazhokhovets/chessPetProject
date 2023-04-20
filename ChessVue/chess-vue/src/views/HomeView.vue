<template>
  <div >

    <Socket />
    <Settings />

  </div>
</template>

<script>

 import Socket from "@/components/Socket";
 import Settings from "@/components/Settings";

    export default {
        name: 'HomeView',
      components: { Socket, Settings},



    }
</script>
