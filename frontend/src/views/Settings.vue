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
      <el-input-number v-model="textInput" :min="2" :max="20"></el-input-number>
    </div>
    <br />
    <el-button type="primary" round @click="doLda">get lda</el-button>
  </b-container>
</template>

<!-- JavaScriptを記述 -->
<script>
import axios from 'axios'
import { BACKEND_URL } from '../../util/const'
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
          name: 'text.xml',
          icon: 'mdi-camera',
          mimeType: 'text/xml',
          msg: '',
        },
        {
          content: null,
          name: 'person.csv',
          icon: 'mdi-message-text-outline',
          mimeType: 'text/csv',
          msg: '',
        },
      ],
    }
  },
  methods: {
    getLda() {
      this.$parent.num_data = Number(this.textInput)
    },
    doLda() {
      const path = BACKEND_URL + '/doLda'
      var params = new URLSearchParams()
      params.append('num', String(this.textInput))
      params.append('xml', this.files[0].name)
      params.append('csv', this.files[1].name)
      axios
        .post(path, params)
        .then((response) => {
          this.status = 'successs'
          console.log(response.data)
          this.files[0].msg = 'Succeses!!'
          console.log(response)
        })
        .catch((error) => {
          console.log(error)
        })
    },
    selected: function (i, e) {
      this.files[i].content = e
      this.files[i].name = e.name
      this.files[i].msg = ''
      console.log(e)
    },
    upload: function (i) {
      const { name, content, mimeType } = this.files[i]
      console.log(name, mimeType)
      if (!content) {
        this.files[i].msg = '*please select file*'
        return
      }
      let path = ''
      if (mimeType == 'text/csv') {
        path = BACKEND_URL + '/upload/csv'
      } else if (mimeType == 'text/xml') {
        path = BACKEND_URL + '/upload/xml'
      }
      this.status = 'now loading...'
      var params = new FormData()
      params.append('file', content, name)
      axios
        .post(path, params)
        .then((response) => {
          this.status = 'successs'
          console.log(response.data)
          this.files[i].msg = 'Succeses!'
          console.log(response)
        })
        .catch((error) => {
          console.log(error)
        })
    },
  },
  created() {},
}
</script>
<!--一行空行を入れてください-->
