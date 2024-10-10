#include "clientch.h"
#include <string>

using namespace std;


ClientCh::ClientCh(QString IP, QObject *parent)
{
    const int lengthIP = 20;
    socket = new QTcpSocket;
    string a = "192.168.0.104";
    QString aaa = "192.168.0.104";
    //const char *forIP = IP.c_str();
    char aa[lengthIP] = {"192.168.0.104"};
    QHostAddress addr(aaa);
    socket -> connectToHost(addr,8888);
    connect (socket,SIGNAL(connected()),SLOT(onConnected()));
    connect (socket,SIGNAL(readyRead()),SLOT(transferData()));
}

ClientCh::~ClientCh()
{
    socket->close();
    delete socket;
}


void ClientCh::onConnected()
{

qDebug() << " ClientCh::onConnected() connected";

    emit myconnected();
    connect(socket,SIGNAL(disconnected()),SLOT(onDisconnect()));
}

void ClientCh::onDisconnected()
{
    emit mydisconnected();
    //socket = 0;
}
void ClientCh::transferData()
{

    QByteArray ba = socket -> readAll();
    mes += ba;
    int size = static_cast<int>(mes[0]);
    int sizewh = static_cast<int>(mes[1]);
    int sizebl= static_cast<int>(mes[2]);
    int sizewhd = static_cast<int>(mes[3]);
    int sizebld = static_cast<int>(mes[4]);

    if (size <= mes.size())
    {
        QList <QPoint> wh;
        QList <QPoint> bl;
        QList <QPoint> whd;
        QList <QPoint> bld;

        for (int i = 0; i < sizewh; ++i)
        {
            wh.push_back(QPoint(mes[5+2*i],mes[5+2*i+1]));
        }
        for (int i = 0; i < sizebl; ++i)
        {
            bl.push_back(QPoint(mes[5 + 2*i + sizewh*2],mes[5 + 2*i + 1 + sizewh*2]));
        }
        for (int i = 0; i < sizewhd; ++i)
        {
            whd.push_back(QPoint(mes[5+2*i + sizewh*2 + sizebl*2],mes[5 + 2*i + 1 + sizewh*2 + sizebl*2]));
        }
        for (int i = 0; i < sizebld; ++i)
        {
            bld.push_back(QPoint(mes[5 + 2*i + sizewh*2 + sizebl*2 + sizewhd*2],mes[5 + 2*i + 1 + sizewh*2 + sizebl*2 + sizewhd*2]));
        }
        emit ServerTurn(wh,bl,whd,bld);
    }
    static int counter=0;
    qDebug() << "Client " << counter++ << " received - " << size << "" << int(mes[1]) << " " << int(mes[2]) << " " << int(mes[3]);

    for ( int i = 0; i < mes.size(); ++i)
    {
        qDebug() << "client received" << int(mes[i]);
    }

    mes = mes.right(mes.size()-mes[0]); // skidaemo rozmir packeta
}

void ClientCh::turn(const QList<QPoint> &whi, const QList<QPoint> &bla, const QList<QPoint> &whid, const QList<QPoint> &blad)
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
        // potim server mae zrobyty z ciogo ReadAll i otrymaty ci dani

        qDebug() << "len = " << len;
        static int counterr=0;
         qDebug() << "Client" << counterr++ << "send - " << int(ba[0]) << " " << int(ba[1]) << "  " << int(ba[2]) << " " << int(ba[3]);
        }

}

