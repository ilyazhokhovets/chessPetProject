<template>
<div class="relative">
 Начальная Позиция
  <input v-model="settings.startingFen" class="feninput" />
  <button  @click="setStartingFenDefault">default</button> <br>
<!--  <button @click="ыу">Сделать текущую позицию начальной</button>-->
  Максимальная глубина
  <input v-model="settings.maxDepth" class="digitinput" > <br>
  Максимальная оценка белых
  <input v-model="settings.maxCpWhite" class="digitinput"> <br>
  Максимальная оценка черных
  <input v-model="settings.maxCpBlack" class="digitinput"> <br>
  Минимальная частота хода
  <input v-model="settings.minAppearancePercent" class="digitinput">  <br>
  Минимальная общая частота
  <input v-model="settings.minAppearancePercentTotal" class="digitinput"> <br>
  <button @click="deldb">delete db</button>
</div>
</template>

<script>
export default {
  name: "Settings",
  created() {
    this.emitEventChanged()
  },
  data() {
    return {
      settings: {
      startingFen: 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1',
      maxDepth: '7',
      maxCpWhite: '150',
      maxCpBlack: '-100',
      minAppearancePercent: '0.05',
      minAppearancePercentTotal: '10000'}
    }
  },
  watch: {
    settings() {
      console.log('w')
      this.emitEventChanged()
    }
  },
  methods: {
    setStartingFen(){
      this.settings.startingFen = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'
    },
    setStartingFenDefault() {
      console.log('ok')
      this.settings.startingFen = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'
      // this.emitEventChanged()
      this.boom()
    },
    async deldb(){
      let data = {

      }

      this.listMove = await fetch(
          `${this.$store.getters.getServerUrl}/move/`,
          {
            method: "POST",
            headers: {
              'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)}
      ).then(response => response.json())
    console.log('done')

    },
    boom (){
      console.log(this.settings)
    },
            emitEventChanged () {
      console.log('e')
              let settings = {
                 startingFen: this.startingFen,
                  maxDepth: this.maxDepth,
                  maxCpWhite: this.maxCpWhite,
                  maxCpBlack: this.maxCpBlack,
                  minAppearancePercent: this.minAppearancePercent,
                  minAppearancePercentTotal: this.minAppearancePercentTotal
              }
                this.$store.commit('setSittings', this.settings)
            }
        }
}

</script>

<style scoped>
div.relative {
  position: absolute;
  top: 80px;
  left: 500px;
  font-size: 18px;
}
.feninput {
  width: 400px;
}
.digitinput{
  width: 50px;
}
</style>