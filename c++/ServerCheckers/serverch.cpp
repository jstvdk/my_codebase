#include "serverch.h"
#include "widget.h"

// ReshetnykV@gmail.com

ServerCh::ServerCh(QObject *parent) : QObject(parent)
{
    server = new QTcpServer();
    connect(server,SIGNAL(newConnection()),SLOT(onConnect())); // koly na server postykayt vikli4etsa slot onConected;
    server -> listen(QHostAddress::Any,8888);
    socket = 0; // zanylae socket sho b tam ne lejalo smittya

   /* SSocket = new QTcpSocket;
    QHostAddress addr("10.42.0.1");
    SSocket -> connectToHost(addr,8888);
    //connect (SSocket,SIGNAL(connected()),SLOT(onConnected()));
    connect (SSocket,SIGNAL(readyRead()),SLOT(transferDataClient())); */

}
ServerCh::~ServerCh()
{
    server->close();
    delete server;
}
void ServerCh::onConnect() // koly postykav server signal newConnection(), koly vidislav shos to ReadyRead();
{
    socket = server -> nextPendingConnection();  // koly servery postykaly, server povertae object tupy socket
    emit myconnected(); // generye vlasniy signal

    // READYREAD - This signal is emitted once every time new data is available for reading from the device.
    //It will only be emitted again once new data is available, such as when a new payload of network data
    //has arrived on your network socket, or when a new block of data has been appended to your device.

    connect(socket,SIGNAL(readyRead()),SLOT(transferData())); // koly otryamlis dani, zapyskaetsa signal ReadyRead
    connect(socket,SIGNAL(disconnected()),SLOT(onDisconnect())); // yaksho poshle signal disconnected to vkly4itsa slot onDisconnect
}

void ServerCh::onDisconnect()
{
    emit mydisconnected();
    socket = 0;
}

void ServerCh::transferData()
{
    QByteArray ba = socket -> readAll();
        mes += ba;
        int size = static_cast<int>(mes[0]);
        int sizewh = static_cast<int>(mes[1]);
        int sizebl= static_cast<int>(mes[2]);
        int sizewhd = static_cast<int>(mes[3]);
        int sizebld = static_cast<int>(mes[4]);

    if(mes[0] <= mes.size())
    {
        QList <QPoint> wh;
        QList <QPoint> bl;
        QList <QPoint> whd;
        QList <QPoint> bld;

        for (int i = 0; i < mes[1]; ++i)
        {
            wh.push_back(QPoint(mes[5+2*i],mes[5+2*i+1]));
        }
        for (int i = 0; i < mes[2]; ++i)
        {
            bl.push_back(QPoint(mes[5 + 2*i + mes[1]*2],mes[5 + 2*i + 1 + mes[1]*2]));
        }
        for (int i = 0; i < mes[3]; ++i)
        {
            whd.push_back(QPoint(mes[5+2*i + mes[1]*2 + mes[2]*2],mes[5 + 2*i + 1 + mes[1]*2 + mes[2]*2]));
        }
        for (int i = 0; i < mes[4]; ++i)
        {
            bld.push_back(QPoint(mes[5 + 2*i + mes[1]*2 + mes[2]*2 + mes[3]*2],mes[5 + 2*i + 1 + mes[1]*2 + mes[2]*2 + mes[3]*2]));
        }

        emit clientTurn(wh,bl,whd,bld);

        static int counter=0;
        qDebug() << "Server "<<counter++<<"received - " << size << " " << int(mes[1]) << " " << int(mes[2]) << "  " << int(mes[3]);

        for ( int i = 0; i < mes.size(); ++i)
        {
            qDebug() << "client received" << int(mes[i]);
        }

        mes = mes.right(mes.size()-mes[0]); // skidaemo rozmir packeta
    }    
}

/*void ServerCh::transferDataClient()
{
        QByteArray ba = SSocket -> readAll();
            mes += ba;
            int size = static_cast<int>(mes[0]);
            int sizewh = static_cast<int>(mes[1]);
            int sizebl= static_cast<int>(mes[2]);
            int sizewhd = static_cast<int>(mes[3]);
            int sizebld = static_cast<int>(mes[4]);

        if(mes[0] <= mes.size())
        {
            QList <QPoint> wh;
            QList <QPoint> bl;
            QList <QPoint> whd;
            QList <QPoint> bld;

            for (int i = 0; i < mes[1]; ++i)
            {
                wh.push_back(QPoint(mes[5+2*i],mes[5+2*i+1]));
            }
            for (int i = 0; i < mes[2]; ++i)
            {
                bl.push_back(QPoint(mes[5 + 2*i + mes[1]*2],mes[5 + 2*i + 1 + mes[1]*2]));
            }
            for (int i = 0; i < mes[3]; ++i)
            {
                whd.push_back(QPoint(mes[5+2*i + mes[1]*2 + mes[2]*2],mes[5 + 2*i + 1 + mes[1]*2 + mes[2]*2]));
            }
            for (int i = 0; i < mes[4]; ++i)
            {
                bld.push_back(QPoint(mes[5 + 2*i + mes[1]*2 + mes[2]*2 + mes[3]*2],mes[5 + 2*i + 1 + mes[1]*2 + mes[2]*2 + mes[3]*2]));
            }

            emit clientTurn(wh,bl,whd,bld);

            static int counter=0;
            qDebug() << "Server "<<counter++<<"received - " << size << " " << int(mes[1]) << " " << int(mes[2]) << "  " << int(mes[3]);
            //mes = mesright(80);
        }
}*/

void ServerCh::turn(const QList<QPoint> &whi, const QList<QPoint> &bla, const QList<QPoint> &whid, const QList<QPoint> &blad)
{
    int n = 5 + 2*whi.size() + 2*bla.size() + 2*whid.size() + 2*blad.size();
    QByteArray ba(n, ' '); // 1 zna4ennya skilky byte, 2 sho tuda poklasty bo nemae constructora z 1 argumentom
    ba[0] = n;
    ba[1] = static_cast<char>(whi.size());
    ba[2] = static_cast<char>(bla.size());
    ba[3] = static_cast<char>(whid.size());
    ba[4] = static_cast<char>(blad.size());
        for (int i = 0; i < whi.size(); i++)
        {
            ba[5+2*i] = whi[i].x();  // zabivae coordinaty x massiv
            ba[5+2*i+1] = whi[i].y(); // zabivae coordinaty y v massiv
        }
        for (int i = 0; i < bla.size(); i++)
        {
            ba[5 + 2*whi.size() + 2*i] = bla[i].x();  // zabivae coordinaty x massiv
            ba[5 + 2*whi.size() + 2*i+1] = bla[i].y();
        }
        for (int i = 0; i < whid.size(); i++)
        {
            ba[5+2*whi.size()+bla.size()*2+2*i] = whid[i].x();
            ba[5+2*whi.size()+bla.size()*2+2*i+1] = whid[i].y();
        }
        for ( int i = 0; i < blad.size(); i++)
        {
            ba[5+2*whi.size()+bla.size()*2+whid.size()*2+2*i] = blad[i].x();
            ba[5+2*whi.size()+bla.size()*2+whid.size()*2+2*i+1] = blad[i].y();
        }

        if (socket != 0) // perevirka 4u proishlo ziednannya
        {
        int len = socket -> write(ba); // zapisye v socket massiv ba
                socket->flush();
        // potim client mae zrobyty z ciogo ReadAll i otrymaty ci dani
        static int counterr=0;

        qDebug() << "len = " << len;
        qDebug() << "Server " << counterr++ << "send - " << int(ba[0]) << " " << int(ba[1]) << "  " << int(ba[2]) << " " << int(ba[3]);
        }
}



