<template>
        <v-dialog
            v-model="dialog"
            max-width="80%"
            >
            <template v-slot:activator="{ on, attrs }">
                <v-list-item v-bind="attrs" v-on="on">
                    <v-list-item-icon>
                        <v-icon>mdi-upload</v-icon>
                    </v-list-item-icon>
                    <v-list-item-title>Upload Data</v-list-item-title>
                </v-list-item>
            </template>

            <v-card color="primary" dark>
                <v-card-title class="text-h5">
                    Upload Data
                </v-card-title>

                <v-card-text>
                    Please update data as a *.csv where the first row are the names of the variables and each row following is an entry.
                </v-card-text>
                <v-container pa-6>
                    <v-file-input show-size truncate-length="50" label="CSV Input" outlined accept=".csv"
                       v-on:change="validate"
                       v-on:click:clear="reset"
                    >
                    </v-file-input>
                    <v-chip-group
                        v-model="selected_labels"
                        column
                        multiple
                        v-if="labels.length < 40"
                    >
                        <v-chip
                        filter
                        v-for="(label, index) in labels"
                        :key="label.name"
                        outlined
                        :color="selected_labels.includes(index) ? 'accent' : 'secondary'"
                        >
                            {{label.text}}
                        </v-chip>
                        
                    </v-chip-group>
                    <v-container pb-4 pl-0 pt-0>
                        <v-chip-group>

                        <v-chip
                            v-if="table == false && labels.length < 40"
                            color="success"
                            v-on:click="selectAll"
                        
                        >
                            <v-avatar left>
                                <v-icon>mdi-checkbox-marked-circle</v-icon>
                            </v-avatar>
                            Select All
                        </v-chip>

                        <v-chip
                            v-if="table == false && labels.length < 40"
                            color="error"
                            v-on:click="deselectAll"
                            pa-2
                        >
                            <v-avatar left>
                                <v-icon>mdi-close-circle</v-icon>
                            </v-avatar>
                            Deselect All
                        </v-chip>
                        </v-chip-group>

                    </v-container>


                    


                    <v-data-table light color="accent" :hidden="table" class="elevation-2" :headers="labels.filter((_, index) => selected_labels.includes(index))" :items="activeEntries">
                        <template v-slot:progress>
                            <v-progress-linear v-show="table" rounded color="secondary" indeterminate height="6" absolute></v-progress-linear>
                        </template>
                        
                        <template v-slot:item="{ item }">
                            <tr>
                                <td v-for="(col, i) in item" :key="i">
                                    {{col.toString().substr(0,6)}}
                                </td>
                            </tr>
                        </template>
                    </v-data-table>
                </v-container>
                

                <v-divider></v-divider>
                <v-card-actions>
                    <v-spacer></v-spacer>
                    <v-btn
                        color="info"
                        text
                        v-on:click="cancel"
                    >
                        Cancel
                    </v-btn>
                    <v-btn
                        color="accent"
                        v-on:click="upload"
                    >
                        Upload
                    </v-btn>
                </v-card-actions>
            </v-card>
            
        
        </v-dialog>
</template>

<script>
import * as d3 from 'd3';

import {Tab} from '@/objs/Tab.js';
import {CSVData} from '@/objs/CSVData.js';

export default {
	data() {
		return {
            ds: null,
            dialog: false,
            table: true,
            labels: [],
            selected_labels: [],
            entries: []
		};
	},
    computed: {
        activeEntries: function() {
            let arr = []
            this.entries.forEach((obj) => {
                let temp = {}
                for(const [key, value] of Object.entries(obj)) {
                    if(this.labels.filter((_, index) => this.selected_labels.includes(index)).map(e => e.text).includes(key)) {
                        temp[key] = value;
                    }
                }
                arr.push(temp);
            })
            return arr;
        }
    },
	methods: {
    selectAll() {
        this.selected_labels = Array.from(Array(this.labels.length).keys());
        console.log(this.selected_labels)
    },
    deselectAll() {
        this.selected_labels = [];
    },
    upload() {
        // this.$store.commit('addTab', new Tab("Test Heatmap", this.ds, Tab.Types.HEATMAP));
        // this.$tabs.push(new Tab("Test Graph", this.ds, Tab.Types.CHART));
        this.reset();
        this.dialog = false;
        console.log("uploading");
        this.$store.commit('addDS', this.ds);
        this.$store.commit('appendTab', Tab.Types.NETWORK);
        this.$store.commit('appendTab', Tab.Types.HEATMAP);
    },
    reset() {
        this.table = true;
        this.labels = [];
        this.selected_labels = [];
        this.entries = [];
    },
    cancel() {
        this.reset();
        this.dialog = false;
    },
    validate(file) {
        if(file) {
            const reader = new FileReader();
            reader.onload = (res) => {
                this.createTable(res.target.result.split(/\r\n|\n\r|\n|\r/));
                let csvData = d3.csvParse(res.target.result);
                this.ds = new CSVData(csvData);
            }
            reader.onerror = (err) => {
                console.log(err);
            }
            reader.readAsText(file);
        }
    },
    async createTable(content) {
        if(content.length > 100) {
            content = content.slice(0,100);
        }
        let headers = content.shift();
        if(headers[0] == '"') {
            this.labels = headers.slice(1, -1).split('","');
        }
        else {
            this.labels = headers.split(',');
        }

        if(this.labels.length > 40) {
            this.labels = [];
            return;
        }
        
        this.labels.forEach((label, index) => {
            this.labels[index] = {text:label , align:'start', sortable:true, value:label}
            this.selected_labels.push(index);
        })
        content.forEach((row) => {
            row = row.split(",");
            if (row.length == this.labels.length) {
                let obj = {}
                row.forEach((entry, index) => {
                    obj[this.labels[index].value] = entry
                })
                this.entries.push(obj)
            }
        })
        this.table = false;
    },
	}
};
</script>
<style scoped>
.v-list-item:hover {
	background-color: #D39F10;
  /* background-color: #ae9142; */
}
</style>
