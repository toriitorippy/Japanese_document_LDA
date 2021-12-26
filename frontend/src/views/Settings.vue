<!-- HTMLを記述 -->
<template>
  <b-container>
    <div class="fortune">
    <br />
      <b-row class="">
        <b-col v-for="(file, i) in files" :key="i">
          <v-card outlined class="pa-2" v-if="!(file.name == 'audio_folder')">
            <v-file-input
              :prepend-icon="file.icon"
              @change="selected(i, $event)"
              :accept="file.mimeType"
              :name="file.name"
              show-size
              truncate-length="20"
              :label="file.name"
            ></v-file-input>
            <v-btn @click="upload(i)">upload</v-btn>
            <div>
              {{ file.msg }}
            </div>
          </v-card>
        </b-col>
      </b-row>
    </div>
    <br />
    <br />
    <p>Enter the number of topics</p>
    <div id="app">
      <el-input-number
        v-model="textInput"
        @change="handleChange"
        :min="2"
        :max="20"
      ></el-input-number>
    </div>
    <br />
    <el-button type="primary" round @click="getLda">get lda</el-button>
  </b-container>
</template>

<!-- JavaScriptを記述 -->
<script>
export default {
  name: 'Settings',
  data() {
    return {
      randomNum: 0,
      status: null,
      textInput: 10,
      files: [
        {
          content: null,
          name: 'mov.mp4',
          icon: 'mdi-camera',
          mimeType: 'video/mp4',
          msg: '',
        },
        {
          content: null,
          name: 'diagram.png',
          icon: 'mdi-chart-bar',
          mimeType: 'image/png',
          msg: '',
        },
        {
          content: null,
          name: 'transcript.csv',
          icon: 'mdi-message-text-outline',
          mimeType: 'text/csv',
          msg: '',
        },
        {
          content: null,
          name: 'apisnote.json',
          icon: 'mdi-file-tree-outline',
          mimeType: 'application/json',
          msg: '',
        },
        {
          content: null,
          name: 'audio_only.m4a',
          icon: 'mdi-music-note',
          mimeType: 'audio/x-m4a',
          msg: '',
        },
        {
          content: null,
          name: 'audio_folder',
          icon: 'mdi-folder-music-outline',
          mimeType: 'audio/x-m4a',
          msg: '',
        },
      ],
    }
  },
  methods: {
    getLda() {
      this.$parent.num_data = Number(this.textInput)
    },
  },
  created() {},
}
</script>
<!--一行空行を入れてください-->
