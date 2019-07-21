clear
clc
close all

X=importdata('trajectory.txt');
U=importdata('traffic lights.txt');

[m,n]=size(X);
n_links=n/2;
figure
hold on
for i=1:n_links
    plot(X(:,2*i-1),'LineWidth',2)
end
title('Vehicular Volumes over Time')
ylabel('x')
xlabel('t')
hold off
% figure
% hold on
% for i=1:n_links
%     plot(X(:,2*i))
% end
% title('controls')
% hold off
figure
hold on
h=4.7;
for i=1:12
    for t=1:m
        rectangle('Position',[t-1,(3*i-3)*h,1,h],'FaceColor',[1-U(t,2*i-1) U(t,2*i-1) 0])
        rectangle('Position',[t-1,(3*i+1-3)*h,1,h],'FaceColor',[1-U(t,2*i) U(t,2*i) 0])
    end
end
for j=1:5
    rectangle('Position',[j*6-0.05,0,0.1,h*35],'FaceColor',[0 0 0])
end
set(gca,...
'YTickLabel','')
xlabel('t')
title('Traffic Lights')
axis([0,34,0,35*h])
hold off
    




