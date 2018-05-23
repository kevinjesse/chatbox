%function [J, grad1, grad2] = costFunction(X, Y, R, theta1, theta2, lambda1, lambda2)
%function [theta1, theta2] = trainLinearReg(XR, YR, R, lambda1, lambda2)


X = full(mmread("X.mm.mtx"));
X = X(1,:);
Y = full(mmread("Y.mm.mtx"));
% U1 = full(mmread("U.mm.mtx"));
% U = U1;
% V1 = full(mmread("V.mm.mtx"));
% V = V1;
% Obs = mmread("sparseN.mm.mtx");
% R = full(Obs');
% R = R(1,:);
% R = X*U*V*Y';


[m, n] = size(R);
%TRAINLINEARREG Trains linear regression given a dataset (X, y) and a
%regularization parameter lambda
%   [theta] = TRAINLINEARREG (X, y, lambda) trains linear regression using
%   the dataset (X, y) and regularization parameter lambda. Returns the
%   trained parameters theta.
%
s = size(X, 2);
t = size(Y, 2);

% Initialize Theta
% l1 = ones(s, 1).* (-.2 + (.2+.2)*rand(s,1));
% l2 = ones(t, 1).*(-.2 + (.2+.2)*rand(t,1)); 
l1=.1;
l2=.1;
iters = 3555;
cost_history = zeros(iters,1);


for i = 1:iters
    
    [U, V] = online_update_weights(X, Y, R, U, V, l1, l2);    
    
    cost = costFunction(X, Y, R, U, V, l1, l2);
    cost_history(i) = cost;
%     if mod(i,10) == 0
%         fprintf("iter: %d | cost: %d\n", i, cost);
%     end
end

R = X*U*V*Y';
[~,NewPredict] = sort(R, 2, 'descend');
%[J, grad1, grad2] = costFunction(X, Y, R, theta1, theta2, lambda1, lambda2);

%function [J, grad1, grad2] = costFunction(X, Y, R, t1, t2, lambda1, lambda2)


