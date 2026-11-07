// Local repair A*: 4-connected grid on two layers; a separate via mask.
#include <algorithm>
#include <cmath>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <queue>
#include <vector>
using namespace std;
int main(int argc,char**argv){
 ifstream f(argv[1],ios::binary);int nx,ny;f.read((char*)&nx,4);f.read((char*)&ny,4);int n=nx*ny,N=2*n;
 vector<unsigned char> blocked(N),via(n),src(N),dst(N);f.read((char*)blocked.data(),N);f.read((char*)via.data(),n);f.read((char*)src.data(),N);f.read((char*)dst.data(),N);
 int xlo=nx,xhi=0,ylo=ny,yhi=0;for(int i=0;i<N;i++)if(dst[i]&&!blocked[i]){int q=i%n,x=q%nx,y=q/nx;xlo=min(xlo,x);xhi=max(xhi,x);ylo=min(ylo,y);yhi=max(yhi,y);}
 auto h=[&](int i){int q=i%n,x=q%nx,y=q/nx;return max(0,max(xlo-x,x-xhi))+max(0,max(ylo-y,y-yhi));};
 vector<int>d(N,INT32_MAX),par(N,-1);using Q=pair<int,int>;priority_queue<Q,vector<Q>,greater<Q>>pq;
 for(int i=0;i<N;i++)if(src[i]&&!blocked[i]){d[i]=0;pq.push({h(i),i});}
 int goal=-1,vis=0;while(!pq.empty()){
 auto [cost,i]=pq.top();pq.pop();if(cost!=d[i]+h(i))continue;vis++;
 if(dst[i]){goal=i;break;}int q=i%n,x=q%nx,y=q/nx;
 int opts[5]={x>0?i-1:-1,x+1<nx?i+1:-1,y>0?i-nx:-1,y+1<ny?i+nx:-1,!via[q]?(i<n?i+n:i-n):-1};
 for(int j:opts)if(j>=0&&!blocked[j]){int nd=d[i]+(abs(i-j)==n?30:1);if(nd<d[j]){d[j]=nd;par[j]=i;pq.push({nd+h(j),j});}}
 }
 cerr<<"visited "<<vis<<" goal "<<goal<<"\n";if(goal<0)return 2;
 vector<int>path;for(int i=goal;i>=0;i=par[i])path.push_back(i);reverse(path.begin(),path.end());ofstream out(argv[2],ios::binary);out.write((char*)path.data(),path.size()*4);return 0;
}
