#!/usr/bin/env python3

import argparse
import sys
import time

class GenericZFitsWriter:
    def __init__(self, writer_id, forward_port):
        self.writer_id = writer_id
        self.forward_port = forward_port
        self.perpetual = False
        self.running = False
        self.interrupted = False

    def setEventType(self, event_type):
        self.event_type = event_type

    def setPerpetualOperations(self, perpetual):
        self.perpetual = perpetual

    def setFileNumberStride(self, stride, instance):
        self.stride = stride
        self.instance = instance

    def setSubsystem(self, subsystem):
        self.subsystem = subsystem

    def setOutputPath(self, output_dir):
        self.output_dir = output_dir

    def addDistantPeer(self, peer):
        # Placeholder for adding a distant peer
        pass

    def setMaxEventsPerFile(self, max_events):
        self.max_events_per_file = max_events

    def setNumEventsPerTile(self, num_events):
        self.num_events_per_tile = num_events

    def setNumCompressionThreads(self, num_threads):
        self.num_comp_threads = num_threads

    def setMaxCompressionMemoryinKB(self, max_mem_kb):
        self.max_comp_mem_kb = max_mem_kb

    def setMaximumFileSizeinKB(self, max_size_kb):
        self.max_file_size_kb = max_size_kb

    def setDefaultCompression(self, scheme):
        self.comp_scheme = scheme

    def setDefaultCompressionBlockSize(self, block_size):
        self.comp_block_size = block_size

    def setHeaderFlushLapse(self, lapse_ms):
        self.head_flush_interval = lapse_ms

    def setSourceName(self, source_name):
        self.source_name = source_name

    def setCameraName(self, camera_name):
        self.camera_name = camera_name

    def setNamingScheme(self, naming_scheme):
        self.naming_scheme = naming_scheme

    def setZombieStreamTimeoutDurationInSeconds(self, timeout_seconds):
        self.zombie_timeout = timeout_seconds

    def setMaxNumWaitingEvents(self, max_events):
        self.max_waiting_events = max_events

    def start(self):
        # Placeholder for starting the writer
        self.running = True
        print("Writer started.")

    def isRunning(self):
        # Placeholder for checking if the writer is running
        return self.running

    def wasInterrupted(self):
        # Placeholder for checking if the writer was interrupted
        return self.interrupted

    def cleanup(self):
        # Placeholder for cleaning up the writer
        self.running = False
        print("Writer cleaned up.")

class L0ZFitsWriter(GenericZFitsWriter):
    pass

class R1ZFitsWriter(GenericZFitsWriter):
    pass

class CTAR1ZFitsWriter(GenericZFitsWriter):
    pass

def main():
    parser = argparse.ArgumentParser(
        description="""
|------------------------------------------------------------------------------|
|---------------------------------ZFITS WRITER---------------------------------|
|-----------------------A compressed FITS writer module------------------------|
|---Subscribes to streams, sorts out incoming events and writes them to disk---|
|------------------------------------------------------------------------------|
Required parameters:
--output_dir
  Directory where to write the FITS files

--input
  ZMQ input streams config(s). e.g. tcp://localhost:1234

Optional arguments:
--id
  Identifier to associate to this writer (for load balancing)

--max_evts_per_file
  Number of events to write to a given file before opening a new one.
  default=100k

--evts_per_tile
  Number of events to group and compress at once. default=100

--num_comp_threads
  Number of threads to use for compressing data. default=0

--max_comp_mem
  Maximum amount of memory in MBytes to use for compression. default=2GB

--max_file_size
  Maximum size of each uncompressed file in MegaBytes. Due to compression actual
  files will probably be smaller. default=2GB

--comp_scheme
  Compression scheme to use. default=zrice. Available schemes are: raw, zlib,
  fact, diffman16, huffman16, doublediffman16, riceman16