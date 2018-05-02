function [g1, g2] = online_update_weights(X, Y, R, U, V, l1, l2)
% theta1 is U
% theta2 is V
% Linear Regression
% grad1 = 0;
% grad2 = 0;

%lr = .0000001; iX
lr = .0000001; %this is good
%lr = .1;

h = X*U*V*Y';
[m,n] = size(h);



grad1 =  2*V*X'*(h-R)*Y + l1*U;
%l1*U;
grad2 =  2*U*X'*(h-R)*Y + l2*V; 
%l2*V;

% grad1 =  (2/m)*X'*(h-R)*Y*V;
% grad2 =  (2/m)*U'*X'*(h-R)*Y;

g1 = U - (grad1*lr);
g2 = V - (grad2*lr);
% g1 = grad1;
% g2 = grad2;
%UNTITLED Summary of this function goes here
%   Detailed explanation goes here

end

