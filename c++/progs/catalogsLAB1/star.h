#ifndef STAR_H
#define STAR_H
#include <fstream>
#include <iostream>
#include <string>
#include <QString>

using namespace std;

class Star
{

private:
    double RA;
    double dec;
    double mRA;
    double mdec;
    double V;
    string Spec;
    double Mag;

public:
    void setRA(double R);
    void setdec(double de);
    void setmRA(double mR);
    void setmdec(double md);
    void setV(double Ve);
    double getRA() const;
    double getdec() const;
    double getmRA() const;
    double getmdec() const;
    double getV() const;
    bool loadFromFile(ifstream &in);

    void setSpec(string spec);
    void setMag(double M);

    string getSpec() const;
    double getMag() const;



    Star();
    ~Star();
};

#endif // STAR_H
