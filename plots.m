X1=importdata('open-loop.txt');
X2=importdata('MPC_centralized.txt');
X3 = importdata('MPC_decentralized.txt');
X4 = importdata('MPC_cooperative.txt');
s=hgexport('readstyle','traffic2');
s.Format = 'jpeg'; %define your png format
figure
plot(X1),xlabel('Time'),ylabel('Vehicular Volumes'),title('Open-Loop Control')
fnam='t1.jpeg';
hgexport(gcf,fnam,s);
figure
plot(X2),xlabel('Time'),ylabel('Vehicular Volumes'),title('Centralized MPC')
fnam='t2.jpeg';
hgexport(gcf,fnam,s);
figure
plot(X3),xlabel('Time'),ylabel('Vehicular Volumes'),title('Decentralized MPC')
fnam='t3.jpeg';
hgexport(gcf,fnam,s);
figure
plot(X4),xlabel('Time'),ylabel('Vehicular Volumes'),title('Cooperative MPC');
fnam='t4.jpeg';
hgexport(gcf,fnam,s);