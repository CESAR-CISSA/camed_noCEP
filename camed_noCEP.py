#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
CAMED (Contextual Anomaly Mitigation for Event-Driven Systems) - noCEP
======================================================================

CAMED is a tool designed to identify anomalous behavior attacks within 
the MQTT protocol.

This is the noCEP version, which does not use CEP (Complex Event
Processing) and instead relies on a machine learning model to analyze
MQTT packets.

======================================================================
"""


from scapy.all import sniff, IP, TCP
from scapy.contrib.mqtt import MQTT
from net_helper import NetworkInterfaceManager
import numpy as np
import pandas as pd
import os
import csv
import pickle
import subprocess


IP_ATTACKER = '172.18.0.20' # Please insert the IP Attacker in case you have change it into ipsee
MODEL_FILE_PATH = 'model/model.pickle'
FILE_OUTPUT_CSV = 'experiments/'+os.environ['RUN']+'.model_output.csv'


def load_model_and_scaler(path):
    with open(path, 'rb') as handle:
        pickle_obj = pickle.load(handle)

    return pickle_obj['model'], pickle_obj['scaler']


model, scaler = load_model_and_scaler('model/model.pickle')


def analisys_packet(data, model, ip_attacker, scaler, srcAddr):
        data = pd.DataFrame([data], columns=['mqtt_messagetype', 'mqtt_messagelength', 'mqtt_flag_passwd'])
        out_cep_scaled = scaler.transform(data)
        model_pred = model.predict(out_cep_scaled)        
        model_pred = [1 if p == -1 else 0 for p in model_pred]

        if ip_attacker == srcAddr:
            is_attack = 1
        else:
            is_attack = 0

        return model_pred[0], is_attack


def write_output_analisys(filename, data):
        try:
            with open(filename, 'a', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(data) 
        except Exception as e:
            print(f"Error adding data to CSV file: {e}")


class MQTTSniffer:
    def __init__(self, iface, sport, dport):
        self.iface = iface
        self.dport = dport
        self.sport = sport
    

    def packet_callback(self, packet):
        if IP in packet and TCP in packet and (packet[TCP].sport == sport or packet[TCP].dport == dport) and MQTT in packet:
            srcAddr = packet[IP].src
            dstAddr = packet[IP].dst
            tcp_time = str(packet[TCP].time)
            mqtt_type = packet[MQTT].type
            # mqtt_qos = packet[MQTT].QOS

            try:
                mqtt_length = packet[MQTT].length
                                
                try:
                    mqtt_passwd = packet[MQTT].passwordflag
                except:
                    mqtt_passwd = 0
                
                data = [mqtt_type, mqtt_length, mqtt_passwd]
                model_pred, is_attack = analisys_packet(data, model, IP_ATTACKER, scaler, srcAddr)
                output_data = [tcp_time, srcAddr, dstAddr, mqtt_type, mqtt_length, mqtt_passwd, model_pred, is_attack]
                write_output_analisys(FILE_OUTPUT_CSV, output_data)
            except AttributeError as e:
                pass
    

    def start_sniffing(self):
        print(f"Capturing packets from interface {iface} on port {dport}...")

        try:
            sniff(iface=self.iface, filter=f"tcp and port {dport}", prn=self.packet_callback)
        except KeyboardInterrupt:
            print("\nIPSee was interrupted.")


def main(iface, sport, dport):
    sniffer = MQTTSniffer(iface, sport, dport)
    sniffer.start_sniffing()


if __name__ == "__main__":
    manager = NetworkInterfaceManager()
    command = "docker network ls | grep mqtt | awk '{print \"br-\"$1}'"
    selected_interface = subprocess.run(command, shell=True, capture_output=True, text=True, check=True)
    selected_interface = selected_interface.stdout.strip()

    iface = selected_interface
    sport = 1883
    dport = 1883

    main(iface, sport, dport)

