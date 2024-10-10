#include "star.h"
#include <iostream>


using namespace std;

double Star::getdec() const
{
    return dec;
}
double Star::getmdec() const
{
    return mdec;
}
double Star::getmRA() const
{
    return mRA;
}
double Star::getRA() const
{
    return RA;
}
double Star::getV() const
{
    return V;
}
void Star::setdec(double de)
{
    dec = de;
}
void Star::setmdec(double md)
{
    mdec = md;
}
void Star::setmRA(double mR)
{
    mRA = mR;
}
void Star::setRA(double R)
{
    RA = R;
}
void Star::setV(double Ve)
{
    V = Ve;
}

void Star::setSpec(string spec)
{
    Spec = spec;
}
string Star::getSpec() const
{
    return Spec;
}

void Star::setMag(double M)
{
    Mag = M;
}
double Star::getMag() const
{
    return Mag;
}
bool Star::loadFromFile(ifstream &in)

{
    if (in.fail())
    {
        return false;
    }
    else
    {
        return true;
    }
}

Star::Star()
{

}
Star::~Star()
{

}
