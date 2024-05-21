/*
 *  Copyright (C) 2024 Callum Gran
 *
 *  This program is free software: you can redistribute it and/or modify
 *  it under the terms of the GNU General Public License as published by
 *  the Free Software Foundation, either version 3 of the License, or
 *  (at your option) any later version.
 *
 *  This program is distributed in the hope that it will be useful,
 *  but WITHOUT ANY WARRANTY; without even the implied warranty of
 *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *  GNU General Public License for more details.
 *
 *  You should have received a copy of the GNU General Public License
 *  along with this program.  If not, see <https://www.gnu.org/licenses/>.
 */
#include <csv.h>
#include <datatype.h>
#include <datetime.h>
#include <lib/list.h>
#include <macros.h>
#include <pthread.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/types.h>
#include <time.h>

void *filter_bad_times_thread(void *args)
{
    FilterThreadData *data = (FilterThreadData *)args;
    const uint16_t node_id = data->dt_data->arr[data->start]->node_id;
    for (size_t i = 0; i < data->len; i++) {
        if (((AbstractData *)data->data[i])->node_id == node_id) {
            bool add = true;
            for (uint16_t j = data->start; j < data->end; j++) {
                if (compare_datetime(&((AbstractData *)data->data[i])->dt,
                                     &data->dt_data->arr[j]->start_dt) >= 0 &&
                    compare_datetime(&((AbstractData *)data->data[i])->dt,
                                     &data->dt_data->arr[j]->end_dt) <= 0) {
                    add = false;
                    break;
                }
            }
            if (add) {
                list_append(data->new_rows, &data->data[i]);
            }
        }
    }

    return NULL;
}

void filter_bad_times(void **data, NodeDownTimeLen *dt_data, List *new_rows, size_t file_len)
{
    NodeDownTime **dt_arr = (dt_data->arr);
    uint32_t start = 0;
    uint16_t curr_node_id = (*dt_arr)->node_id;
    for (uint32_t i = 0; i < dt_data->len; i++) {
        NodeDownTime *curr = dt_arr[i];
        if (curr->node_id != curr_node_id) {
            FilterThreadData *args = malloc(sizeof(FilterThreadData));
            args->start = start;
            args->end = i - 1;
            args->data = data;
            args->dt_data = dt_data;
            args->new_rows = new_rows;
            args->len = file_len;
            filter_bad_times_thread(args);
            start = i;
            curr_node_id = curr->node_id;
        }
    }
}

/* USB Modem Events Start */

typedef struct usbmodem_data_t {
    DateTime dt;
    uint16_t node_id;
    bool state;
    double value;
} USBModemData;

void parse_usb_modem_line(char *line, void *data, int i)
{
    USBModemData **usb_data = (USBModemData **)data;
    char *save_ptr = NULL;
    char *date = strtok_r(line, ",", &save_ptr);
    parse_date_time(&usb_data[i]->dt, date);

    char *node_id = strtok_r(NULL, ",", &save_ptr);
    usb_data[i]->node_id = atoi(node_id);
    strtok_r(NULL, ",", &save_ptr);
    usb_data[i]->state = strcmp(strtok_r(NULL, ",", &save_ptr), "UP") == 0 ? true : false;
    usb_data[i]->value = atof(strtok_r(NULL, ",", &save_ptr));
}

GEN_FUNCTION(usbmodem_parse_print, USBModemData, "operator/metadata_usbmodem_events.csv",
             "time_filtered/metadata_usbmodem_events.csv", 20114,
             "ts,node_id,network_id,usbmodem_state,usbmodem_value\n", parse_usb_modem_line,
             "%s,%d,%d,%s,%f\n", date, (*row)->node_id, 2, (*row)->state ? "UP" : "DOWN",
             (*row)->value);

/* USB Modem Events End */

/* Band Start */

GEN_STRUCT(BandData, uint16_t, band);

GEN_FUNCTION(band_1min_parse_print, BandData, "operator/metadata_band_1min_bin.csv",
             "time_filtered/metadata_band_1min_bin.csv", 2126380,
             "ts,node_id,network_id,band\n", parse_BandData_line, "%s,%d,%d,%d\n", date,
             (*row)->node_id, 2, (*row)->band);

GEN_FUNCTION(band_events_parse_print, BandData, "operator/metadata_band_events.csv",
             "time_filtered/metadata_band_events.csv", 53938, "ts,node_id,network_id,band\n",
             parse_BandData_line, "%s,%d,%d,%d\n", date, (*row)->node_id, 2, (*row)->band);

/* Band End */

/* Packet Loss Start */
GEN_STRUCT(PacketLossData, uint8_t, service_id, uint16_t, scnt, uint16_t, rcnt, double, rtt);

GEN_FUNCTION(packet_loss_raw_1sec_parse_print, PacketLossData,
             "operator/packetloss_rtt_rawdata_1sec_bins.csv",
             "time_filtered/packetloss_rtt_rawdata_1sec_bins.csv", 114806375,
             "ts,node_id,network_id,service_id,scnt,rcnt,rtt\n", parse_PacketLossData_line,
             "%s,%d,%d,%d,%d,%d,%f\n", date, (*row)->node_id, 2, (*row)->service_id, (*row)->scnt,
             (*row)->rcnt, (*row)->rtt);

GEN_FUNCTION(packet_loss_raw_5min_parse_print, PacketLossData,
             "operator/packetloss_rtt_rawdata_5min_bins.csv",
             "time_filtered/packetloss_rtt_rawdata_5min_bins.csv", 386177,
             "ts,node_id,network_id,service_id,scnt,rcnt,rtt_avg\n", parse_PacketLossData_line,
             "%s,%d,%d,%d,%d,%d,%f\n", date, (*row)->node_id, 2, (*row)->service_id, (*row)->scnt,
             (*row)->rcnt, (*row)->rtt);

GEN_FUNCTION(packet_loss_5min_parse_print, PacketLossData, "operator/packetloss_rtt_5min_bins.csv",
             "time_filtered/packetloss_rtt_5min_bins.csv", 340857,
             "ts,node_id,network_id,service_id,scnt,rcnt,rtt_avg\n", parse_PacketLossData_line,
             "%s,%d,%d,%d,%d,%d,%f\n", date, (*row)->node_id, 2, (*row)->service_id, (*row)->scnt,
             (*row)->rcnt, (*row)->rtt);
/* Packet Loss End */

/* CE Level Start */
GEN_STRUCT(CELevelData, int16_t, celevel);

GEN_FUNCTION(celevel_1min_parse_print, CELevelData, "operator/metadata_celevel_1min_bin.csv",
             "time_filtered/metadata_celevel_1min_bin.csv", 2126385,
             "ts,node_id,network_id,celevel\n", parse_CELevelData_line, "%s,%d,%d,%d\n", date,
             (*row)->node_id, 2, (*row)->celevel);

GEN_FUNCTION(celevel_events_parse_print, CELevelData, "operator/metadata_celevel_events.csv",
             "time_filtered/metadata_celevel_events.csv", 10094,
             "ts,node_id,network_id,celevel\n", parse_CELevelData_line, "%s,%d,%d,%d\n", date,
             (*row)->node_id, 2, (*row)->celevel);
/* CE Level End */

/* Cid Start */
GEN_STRUCT(CidData, int16_t, cid);

GEN_FUNCTION(cid_1min_parse_print, CidData, "operator/metadata_cid_1min_bin.csv",
             "time_filtered/metadata_cid_1min_bin.csv", 2126385,
             "ts,node_id,network_id,cid\n", parse_CidData_line, "%s,%d,%d,%d\n", date,
             (*row)->node_id, 2, (*row)->cid);

GEN_FUNCTION(cid_events_parse_print, CidData, "operator/metadata_cid_events.csv",
             "time_filtered/metadata_cid_events.csv", 10115, "ts,node_id,network_id,cid\n",
             parse_CidData_line, "%s,%d,%d,%d\n", date, (*row)->node_id, 2, (*row)->cid);
/* Cid Level End */

/* Device State Start */
GEN_STRUCT(DeviceStateData, uint16_t, device_state);

GEN_FUNCTION(device_state_1min_parse_print, DeviceStateData,
             "operator/metadata_device_state_1min_bin.csv",
             "time_filtered/metadata_device_state_1min_bin.csv", 2126380,
             "ts,node_id,network_id,device_state\n", parse_DeviceStateData_line, "%s,%d,%d,%d\n",
             date, (*row)->node_id, 2, (*row)->device_state);

GEN_FUNCTION(device_state_events_parse_print, DeviceStateData,
             "operator/metadata_device_state_events.csv",
             "time_filtered/metadata_device_state_events.csv", 38320,
             "ts,node_id,network_id,device_state\n", parse_DeviceStateData_line, "%s,%d,%d,%d\n",
             date, (*row)->node_id, 2, (*row)->device_state);

/* Device State End */

/* Earfcn Start */
GEN_STRUCT(EarfcnData, uint16_t, earfcn);

GEN_FUNCTION(earfcn_1min_parse_print, EarfcnData, "operator/metadata_earfcn_1min_bin.csv",
             "time_filtered/metadata_earfcn_1min_bin.csv", 2126380,
             "ts,node_id,network_id,earfcn\n", parse_EarfcnData_line, "%s,%d,%d,%d\n", date,
             (*row)->node_id, 2, (*row)->earfcn);

GEN_FUNCTION(earfcn_events_parse_print, EarfcnData, "operator/metadata_earfcn_events.csv",
             "time_filtered/metadata_earfcn_events.csv", 21836,
             "ts,node_id,network_id,earfcn\n", parse_EarfcnData_line, "%s,%d,%d,%d\n", date,
             (*row)->node_id, 2, (*row)->earfcn);
/* Earfcn End */

/* Imsi Start */
GEN_STRUCT(ImsiData, uint64_t, imsi);

GEN_FUNCTION(imsi_1min_parse_print, ImsiData, "operator/metadata_imsi_1min_bin.csv",
             "time_filtered/metadata_imsi_1min_bin.csv", 2126380,
             "ts,node_id,network_id,imsi\n", parse_ImsiData_line, "%s,%d,%d,%lu\n", date,
             (*row)->node_id, 2, (*row)->imsi);

GEN_FUNCTION(imsi_events_parse_print, ImsiData, "operator/metadata_imsi_events.csv",
             "time_filtered/metadata_imsi_events.csv", 10094, "ts,node_id,network_id,imsi\n",
             parse_ImsiData_line, "%s,%d,%d,%lu\n", date, (*row)->node_id, 2, (*row)->imsi);
/* Imsi End */

/* Ipaddr Start */
typedef struct ipaddr_data_t {
    DateTime dt;
    uint16_t node_id;
    bool state;
} IpaddrData;

void parse_IpaddrData_line(char *line, void *data, int i)
{
    IpaddrData **usb_data = (IpaddrData **)data;
    char *save_ptr = NULL;
    char *date = strtok_r(line, ",", &save_ptr);
    parse_date_time(&usb_data[i]->dt, date);

    char *node_id = strtok_r(NULL, ",", &save_ptr);
    usb_data[i]->node_id = atoi(node_id);
    strtok_r(NULL, ",", &save_ptr);
    usb_data[i]->state = strcmp(strtok_r(NULL, ",", &save_ptr), "UP") == 0 ? true : false;
}

GEN_FUNCTION(ipaddr_1min_parse_print, IpaddrData, "operator/metadata_ipaddr_1min_bin.csv",
             "time_filtered/metadata_ipaddr_1min_bin.csv", 1695169,
             "ts,node_id,network_id,ipaddr_state\n", parse_IpaddrData_line, "%s,%d,%d, %s\n", date,
             (*row)->node_id, 2, (*row)->state ? "UP" : "DOWN");

GEN_FUNCTION(ipaddr_events_parse_print, IpaddrData, "operator/metadata_ipaddr_events.csv",
             "time_filtered/metadata_ipaddr_events.csv", 15661,
             "ts,node_id,network_id,ipaddr_state\n", parse_IpaddrData_line, "%s,%d,%d,%s\n", date,
             (*row)->node_id, 2, (*row)->state ? "UP" : "DOWN");
/* Ipaddr End */

/* Lac Start */
GEN_STRUCT(LacData, uint16_t, lac);

GEN_FUNCTION(lac_1min_parse_print, LacData, "operator/metadata_lac_1min_bin.csv",
             "time_filtered/metadata_lac_1min_bin.csv", 2126385,
             "ts,node_id,network_id,lac\n", parse_LacData_line, "%s,%d,%d,%d\n", date,
             (*row)->node_id, 2, (*row)->lac);

GEN_FUNCTION(lac_events_parse_print, LacData, "operator/metadata_lac_events.csv",
             "time_filtered/metadata_lac_events.csv", 10094, "ts,node_id,network_id,lac\n",
             parse_LacData_line, "%s,%d,%d,%d\n", date, (*row)->node_id, 2, (*row)->lac);
/* Lac End */

/* LTE Frequency Start */
GEN_STRUCT(LteFrequencyData, uint16_t, lte_frequency);

GEN_FUNCTION(lte_frequency_1min_parse_print, LteFrequencyData,
             "operator/metadata_lte_freq_1min_bin.csv",
             "time_filtered/metadata_lte_freq_1min_bin.csv", 2126380,
             "ts,node_id,network_id,lte_freq\n", parse_LteFrequencyData_line, "%s,%d,%d,%d\n", date,
             (*row)->node_id, 2, (*row)->lte_frequency);

GEN_FUNCTION(lte_frequency_events_parse_print, LteFrequencyData,
             "operator/metadata_lte_freq_events.csv",
             "time_filtered/metadata_lte_freq_events.csv", 53938,
             "ts,node_id,network_id,lte_freq\n", parse_LteFrequencyData_line, "%s,%d,%d,%d\n", date,
             (*row)->node_id, 2, (*row)->lte_frequency);
/* LTE Frequency End */

/* Operator Start */
GEN_STRUCT(OperatorData, uint16_t, operator);

GEN_FUNCTION(operator_1min_parse_print, OperatorData, "operator/metadata_oper_1min_bin.csv",
             "time_filtered/metadata_oper_1min_bin.csv", 2126385,
             "ts,node_id,network_id,operator\n", parse_OperatorData_line, "%s,%d,%d,%d\n", date,
             (*row)->node_id, 2, (*row)->operator);

GEN_FUNCTION(operator_events_parse_print, OperatorData, "operator/metadata_oper_events.csv",
             "time_filtered/metadata_oper_events.csv", 10094,
             "ts,node_id,network_id,operator\n", parse_OperatorData_line, "%s,%d,%d,%d\n", date,
             (*row)->node_id, 2, (*row)->operator);
/* Operator End */

/* RSRP Start */
GEN_STRUCT(RSRPData, int16_t, rsrp);

GEN_FUNCTION(rsrp_1min_parse_print, RSRPData, "operator/metadata_rsrp_1min_bin.csv",
             "time_filtered/metadata_rsrp_1min_bin.csv", 1987526,
             "ts,node_id,network_id,rsrp\n", parse_RSRPData_line, "%s,%d,%d,%d\n", date,
             (*row)->node_id, 2, (*row)->rsrp);

GEN_FUNCTION(rsrp_events_parse_print, RSRPData, "operator/metadata_rsrp_events.csv",
             "time_filtered/metadata_rsrp_events.csv", 14032772,
             "ts,node_id,network_id,rsrp\n", parse_RSRPData_line, "%s,%d,%d,%d\n", date,
             (*row)->node_id, 2, (*row)->rsrp);
/* RSRP End */

/* RSRQ Start */
GEN_STRUCT(RSRQData, int16_t, rsrq);

GEN_FUNCTION(rsrq_1min_parse_print, RSRQData, "operator/metadata_rsrq_1min_bin.csv",
             "time_filtered/metadata_rsrq_1min_bin.csv", 1987526,
             "ts,node_id,network_id,rsrq\n", parse_RSRQData_line, "%s,%d,%d,%d\n", date,
             (*row)->node_id, 2, (*row)->rsrq);

GEN_FUNCTION(rsrq_events_parse_print, RSRQData, "operator/metadata_rsrq_events.csv",
             "time_filtered/metadata_rsrq_events.csv", 25497870,
             "ts,node_id,network_id,rsrq\n", parse_RSRQData_line, "%s,%d,%d,%d\n", date,
             (*row)->node_id, 2, (*row)->rsrq);
/* RSRQ End */

/* RSSI Start */
GEN_STRUCT(RSSIData, int16_t, rssi);

GEN_FUNCTION(rssi_1min_parse_print, RSSIData, "operator/metadata_rssi_1min_bin.csv",
             "time_filtered/metadata_rssi_1min_bin.csv", 2126380,
             "ts,node_id,network_id,rssi\n", parse_RSSIData_line, "%s,%d,%d,%d\n", date,
             (*row)->node_id, 2, (*row)->rssi);

GEN_FUNCTION(rssi_events_parse_print, RSSIData, "operator/metadata_rssi_events.csv",
             "time_filtered/metadata_rssi_events.csv", 18973659,
             "ts,node_id,network_id,rssi\n", parse_RSSIData_line, "%s,%d,%d,%d\n", date,
             (*row)->node_id, 2, (*row)->rssi);
/* RSSI End */

/* Submode Start */
GEN_STRUCT(SubmodeData, uint8_t, submode);

GEN_FUNCTION(submode_1min_parse_print, SubmodeData, "operator/metadata_submode_1min_bin.csv",
             "time_filtered/metadata_submode_1min_bin.csv", 2125013,
             "ts,node_id,network_id,submode\n", parse_SubmodeData_line, "%s,%d,%d,%d\n", date,
             (*row)->node_id, 2, (*row)->submode);

GEN_FUNCTION(submode_events_parse_print, SubmodeData, "operator/metadata_submode_events.csv",
             "time_filtered/metadata_submode_events.csv", 72192,
             "ts,node_id,network_id,submode\n", parse_SubmodeData_line, "%s,%d,%d,%d\n", date,
             (*row)->node_id, 2, (*row)->submode);
/* Submode End */

/* TX Power Start */
GEN_STRUCT(TXPowerData, int16_t, tx_power);

GEN_FUNCTION(tx_power_1min_parse_print, TXPowerData, "operator/metadata_tx_power_1min_bin.csv",
             "time_filtered/metadata_tx_power_1min_bin.csv", 2126380,
             "ts,node_id,network_id,tx_power\n", parse_TXPowerData_line, "%s,%d,%d,%d\n", date,
             (*row)->node_id, 2, (*row)->tx_power);

GEN_FUNCTION(tx_power_events_parse_print, TXPowerData, "operator/metadata_tx_power_events.csv",
             "time_filtered/metadata_tx_power_events.csv", 10094,
             "ts,node_id,network_id,tx_power\n", parse_TXPowerData_line, "%s,%d,%d,%d\n", date,
             (*row)->node_id, 2, (*row)->tx_power);
/* TX Power End */

int main(void)
{
    NodeDownTimeLen *mode_data = parse_mode_file();

    if (mode_data) {
        printf("Successfully parsed mode file!\n");
    } else {
        fprintf(stderr, "Error parsing mode file :(!\n");
        exit(1);
    }

    // usbmodem_parse_print(mode_data);

    // band_1min_parse_print(mode_data);

    // band_events_parse_print(mode_data);

    // packet_loss_raw_1sec_parse_print(mode_data);

    // packet_loss_raw_5min_parse_print(mode_data);

    // packet_loss_5min_parse_print(mode_data);

    // celevel_1min_parse_print(mode_data);

    // celevel_events_parse_print(mode_data);

    // cid_1min_parse_print(mode_data);

    // cid_events_parse_print(mode_data);

    // device_state_1min_parse_print(mode_data);

    // device_state_events_parse_print(mode_data);

    // earfcn_1min_parse_print(mode_data);

    // earfcn_events_parse_print(mode_data);

    // imsi_1min_parse_print(mode_data);

    // imsi_events_parse_print(mode_data);

    // ipaddr_1min_parse_print(mode_data);

    // ipaddr_events_parse_print(mode_data);

    // lac_1min_parse_print(mode_data);

    // lac_events_parse_print(mode_data);

    // lte_frequency_1min_parse_print(mode_data);

    lte_frequency_events_parse_print(mode_data);

    operator_1min_parse_print(mode_data);

    operator_events_parse_print(mode_data);

    rsrp_1min_parse_print(mode_data);

    rsrp_events_parse_print(mode_data);

    rsrq_1min_parse_print(mode_data);

    rsrq_events_parse_print(mode_data);

    rssi_1min_parse_print(mode_data);

    rssi_events_parse_print(mode_data);

    submode_1min_parse_print(mode_data);

    submode_events_parse_print(mode_data);

    tx_power_1min_parse_print(mode_data);

    tx_power_events_parse_print(mode_data);

    for (size_t i = 0; i < mode_data->len; i++) {
        free(mode_data->arr[i]);
    }

    free(mode_data->arr);
    free(mode_data);

    return 0;
}