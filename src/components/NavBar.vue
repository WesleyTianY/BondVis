<template>
      <v-navigation-drawer
        app
        permanent
        expand-on-hover
        color="primary"
        dark
      >
        <v-list>
          <v-list-item>
          <v-list-item-icon>
            <v-img src="../assets/ND_monogram_gold_S.png" max-height="25" max-width="25"></v-img>
          </v-list-item-icon> 
          </v-list-item>  
          <v-list-item link v-on:click="gotoLab" >
            <v-list-item-content>
              <!-- TO DO Make it smooth -->
              <v-list-item-title class="text-h6">
                FA VIS
              </v-list-item-title>
              <v-list-item-subtitle>LAMBS Lab</v-list-item-subtitle>
            </v-list-item-content>
          </v-list-item>
        </v-list>

        <v-divider></v-divider>

        <v-list
          nav
        >
          <Upload></Upload>
          <!-- <v-list-item>
            <v-list-item-icon>
              <v-icon>mdi-file-table-box</v-icon>
            </v-list-item-icon>
            <v-list-item-title>Manage Data</v-list-item-title>
          </v-list-item> -->
        </v-list>
      </v-navigation-drawer>
</template>

<script>
import Upload from '@/navcomponents/Upload.vue';

export default {
  components: {
    Upload,
  },
	data() {
		return {

		};
	},
	methods: {
    gotoLab () {
      window.location.href = "https://lambslab.nd.edu/"
    },
    test() {
      console.log("hello world")
    },
    update() {
      this.$emit('newtab');
    }
	}
};
</script>

