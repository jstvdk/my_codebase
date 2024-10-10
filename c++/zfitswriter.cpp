/**
* @file ExecZFitsWriter.cpp
*
* @brief program wrapper for the ZFitsWriter class
*
* @since   Sep 16, 2014
* @author Etienne Lyard
* @author Dirk Hoffmann -CPPM-, November 2015
*
* $Id$
*/

#include "ZFitsWriter.h"
#include "ConfigService.h"

#include <unistd.h>
#include <cstdlib>
#include <string>
#include <vector>

#include "ProtoDataModel.pb.h"

using namespace std;
using namespace DAQ;
using std::string;
using ADH::ColoredOutput::red;
using ADH::ColoredOutput::no_color;
using namespace ADH::Conf;

int main(int argc, char** argv)
{


  /*******************************************************
   **************** PARSE COMMAND LINE *******************
   *******************************************************/


   ConfigService config(
   "|------------------------------------------------------------------------------|\n"
   "|---------------------------------ZFITS WRITER---------------------------------|\n"
   "|-----------------------A compressed FITS writer module------------------------|\n"
   "|---Subscribes to streams, sorts out incoming events and writes them to disk---|\n"
   "|------------------------------------------------------------------------------|\n"
   "Required parameters:\n"+
    green+"--output_dir\n"+no_color+
          "  Directory where to write the FITS files\n\n"+
    green+"--input\n"+no_color+
          "  ZMQ input streams config(s). e.g. tcp://localhost:1234\n"+
    "\n"
    "Optional arguments:\n"+
    green+"--id\n"+no_color+
          "  Identifier to associate to this writer (for load balancing)\n\n"+
    green+"--max_evts_per_file\n"+no_color+
          "  Number of events to write to a given file before opening a new one.\n"
          "  default=100k\n\n"+
    green+"--evts_per_tile\n"+no_color+
          "  Number of events to group and compress at once. default=100\n\n"+
    green+"--num_comp_threads\n"+no_color+
          "  Number of threads to use for compressing data. default=0\n\n"+
    green+"--max_comp_mem\n"+no_color+
          "  Maximum amount of memory in MBytes to use for compression. default=2GB\n\n"+
    green+"--max_file_size\n"+no_color+
          "  Maximum size of each uncompressed file in MegaBytes. Due to compression actual\n"
          "  files will probably be smaller. default=2GB\n\n"+
    green+"--comp_scheme\n"+no_color+
          "  Compression scheme to use. default=zrice. Available schemes are: raw, zlib,\n"
          "  fact, diffman16, huffman16, doublediffman16, riceman16, factrice, ricefact, \n"
          "  rrice, rice,lzo, zrice, zrice32, lzorice, zstdX.\n\n"+
    green+"--comp_block_size\n"+no_color+
          "  Size of the the blocks to use for compression in MBytes. Increase this value\n"
          "  in case  an exception is raised because of blocks too small. default=2880kB\n\n"+
    green+"--head_flush_inter\n"+no_color+
          "  Duration in milliseconds between two flush of the files header.\n"
          "  Default is 10 seconds, 0 means no flushing at all.\n\n"+
    green+"--loop\n"+no_color+
          "  loops infinitely after a run has stopped and continue writing.\n\n"+
    green+"--source\n"+no_color+
          "  Add a source name to the file header, e.g. a run type, a source name...\n\n"+
    green+"--camera\n"+no_color+
          "  Override the data producer name, e.g. NECTAR01.\n\n" +
    green+"--naming\n"+no_color+
          "  Naming scheme. default or nectar for now.\n\n" +
    green+"--zombie_timeout\n"+no_color+
          "  Duration in seconds before declaring a stream producing no data a zombie.\n"
          "  Default is 10 seconds.\n\n"+
    green+"--max_waiting_evts\n"+no_color+
          "  Max. number of events waiting to be written before flushing the queue\n"
          "  out-of-order. Default is 10k.\n\n"+
    green+"--events_type\n"+no_color+
          "  Which type of events to write: L0, ProtoR1 or CTAR1. Default is L0.\n"+
    green+"--forward_port\n"+no_color+
          "  Which port should forwarded events be served. default=0, aka no forwarding\n"+
    green+"--instance\n"+no_color+
          "  Instance number that we will start from for numbering output files\n"+
    green+"--stride\n"+no_color+
          "  Instance stride, i.e. increment between two files numbers\n"+
    green+"--subsystem\n"+no_color+
          "  Name of the subsystem, used to build output path and filename\n"
   "Note: arguments output_dir and input can be passed as first and second args\n"
   "      without their switch\n"
   );

   config.addDefaultArg("output_dir");
   config.addDefaultArg("input");
   config.setDefaultValue("id", "0");

   config.addPossibleArg("max_evts_per_file");
   config.addPossibleArg("evts_per_tile");
   config.addPossibleArg("num_comp_threads");
   config.addPossibleArg("max_comp_mem");
   config.addPossibleArg("max_file_size");
   config.addPossibleArg("comp_scheme");
   config.addPossibleArg("comp_block_size");
   config.addPossibleArg("head_flush_inter");
   config.addPossibleArg("loop");
   config.addPossibleArg("source");
   config.addPossibleArg("naming");
   config.addPossibleArg("camera");
   config.addPossibleArg("zombie_timeout");
   config.addPossibleArg("max_waiting_evts");
   config.addPossibleArg("events_type");
   config.addPossibleArg("forward_port");
   config.addPossibleArg("instance");
   config.addPossibleArg("stride");
   config.addPossibleArg("subsystem");

   if (!config.parseArgument(argc, argv)) return -1;


  /*******************************************************
   ***********GET A GENERIC WRITER OBJECT AND*************
   ********SPECIALIZE IT TO THE DESIRE EVENT TYPE*********
   *******************************************************/


   uint32 forward_port = 0;
   if (config.has("forward_port"))
   {
       forward_port = config.get<uint32>("forward_port");
       cout << "Will forward events on port " << forward_port << endl;
   }

   GenericZFitsWriter* writer;

   if (config.has("events_type") && config.get<string>("events_type") == "ProtoR1")
   {
       writer = new R1ZFitsWriter(config.get<string>("id"), forward_port);
       writer->setEventType(GenericZFitsWriter::ProtoR1);
   }
   else if (config.has("events_type") && config.get<string>("events_type") == "CTAR1")
   {
       writer = new CTAR1ZFitsWriter(config.get<string>("id"), forward_port);
       writer->setEventType(GenericZFitsWriter::CTAR1);
   }
   else
   {
       writer = new L0ZFitsWriter(config.get<string>("id"), forward_port);
       writer->setEventType(GenericZFitsWriter::L0);
   }

  /*******************************************************
   ****************CONFIGURE WRITER***********************
   *******************************************************/
   if (config.has("loop"))
       writer->setPerpetualOperations(true);

   if (config.has("instance"))
       if (!config.has("stride"))
       {
           cout << "Must provide --stride along with --instance. Aborting." << endl;
           return -1;
       }
   if (config.has("stride"))
       if (!config.has("instance"))
       {
           cout << "Must provide --instance along with --stride. Aborting." << endl;
           return -1;
       }
   if (config.has("stride") && config.has("instance"))
   {
       int32 stride = config.get<int32>("stride");
       int32 instance = config.get<int32>("instance");
       cout << "Will write files " << instance << "," << instance+stride;
       cout << "," << instance+stride+stride << "..." << endl;
       writer->setFileNumberStride(config.get<int32>("stride"),
                                   config.get<int32>("instance"));

   }

   if (config.has("subsystem"))
   {
       writer->setSubsystem(config.get<string>("subsystem"));
   }


   //Output directory fghf fe g
   writer->setOutputPath(config.get<string>("output_dir"));

   //Input stream(s) configuration, e.g. tcp://localhost:1234
   vector<string> inputs = config.getVector<string>("input");
   for (auto it=inputs.begin(); it!=inputs.end(); it++)
       writer->addDistantPeer(*it);

   //Maximum number of events written to a single file
   if (config.has("max_evts_per_file"))
       writer->setMaxEventsPerFile(config.get<int32>("max_evts_per_file"));

   //Number of events per tile, i.e. number of events compressed in a single bunch
   if (config.has("evts_per_tile"))
       writer->setNumEventsPerTile(config.get<int32>("evts_per_tile"));

   //Number of threads to use for compression only
   if (config.has("num_comp_threads"))
       writer->setNumCompressionThreads(config.get<int32>("num_comp_threads"));

   //Maximum amount of memory to use during compression
   if (config.has("max_comp_mem"))
       writer->setMaxCompressionMemoryinKB(config.get<int32>("max_comp_mem") * 1024);

   //Maximum size of each file (uncompressed)
   if (config.has("max_file_size"))
       writer->setMaximumFileSizeinKB(config.get<int32>("max_file_size") * 1024);

   //Compression scheme to use
   if (config.has("comp_scheme"))
       writer->setDefaultCompression(config.get<string>("comp_scheme"));

   //Size of memory blocks used to compress data. Must be greater than the maximum size
   //of a given block. Typically > evts_per_tile * size_of_one_event
   if (config.has("comp_block_size"))
       writer->setDefaultCompressionBlockSize(config.get<int32>("comp_block_size"));

   //How often should files headers be flushed to disk
   //useful to read the data while the current file is not closed yet
   if (config.has("head_flush_inter"))
       writer->setHeaderFlushLapse(config.get<int32>("head_flush_inter"));

   //Name of the observed source
   if (config.has("source"))
       writer->setSourceName(config.get<string>("source"));

   //Name of the camera producing the data. Usually taken from the ZMQ stream
   if (config.has("camera"))
       writer->setCameraName(config.get<string>("camera"));

   //Which naming scheme to use when creating new files
   if (config.has("naming"))
   {
       if (config.get<string>("naming") == "nectar")
           writer->setNamingScheme(GenericZFitsWriter::NECTAR);
       else if (config.get<string>("naming") == "lst")
           writer->setNamingScheme(GenericZFitsWriter::LST);
       else
           if (config.get<string>("naming") != "default")
               throw runtime_error("Error: unknown files naming scheme. "
                                   "Possible args are lst, nectar or default");
   }

   //set maximum waiting time before calling a stream that does not produce data a zombie
   if (config.has("zombie_timeout"))
       writer->setZombieStreamTimeoutDurationInSeconds(config.get<uint64>("zombie_timeout"));

   //maximum number of events waiting in memory before they are flushed to disk
   if (config.has("max_waiting_evts"))
       writer->setMaxNumWaitingEvents(config.get<uint32>("max_waiting_evts"));


  /*******************************************************
   ***********************RUN !***************************
   *******************************************************/
   writer->start();

   while (writer->isRunning())
       sleep(1);


  /*******************************************************
   ********************RUN HAS ENDED**********************
   ***********CLEANUP AND EXIT OR START OVER**************
   *******************************************************/


   if (! config.has("loop") || writer->wasInterrupted())
   {
       google::protobuf::ShutdownProtobufLibrary();
       delete writer;
       return 0;
   }

//    cout << "Starting over..." << endl;
//    delete writer;
//    execv(argv[0], argv);
   /* Never reached */

   return 0;
}

/* Some initialisation for vi(m) to comply to this file's style.
* vim: ts=4 expandtab
*/