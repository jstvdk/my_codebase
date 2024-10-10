#include "widget.h"
#include <QApplication>
#include "star.h"
#include <fstream>
#include <QDebug>
#include <QString>

using namespace std;

void readData();

int main(int argc, char *argv[])
{
    QApplication a(argc, argv);
    Widget w;
    w.show();

    //readData();


    return a.exec();
}

void readData()
{
   /* const int N = 181731;
        Star stars[N];
        int i = 0;
        QString Buffer;
        ifstream in; in.open("/home/jstvdk/data/ppm1.txt");

        if(!in)
        {
            cerr << "Cannot open file";
        }

        while (in)
        {
            getline(in,Buffer);
            if(Buffer.length() < 1)
                break;
            QString formag = Buffer.substr(20,4);
            double mag = atof(formag.c_str());

            QString forspec = Buffer.substr(25,2);

            stars[i].setSpec(forspec);
            stars[i].setMag(mag);

           //cout << "Spectral type is - " << stars[i].getSpec() << " Magnitude is - " << stars[i].getMag() << endl;
        }

           in.close();*/
}
