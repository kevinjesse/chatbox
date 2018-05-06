%function [J, grad1, grad2] = costFunction(X, Y, R, theta1, theta2, lambda1, lambda2)
%function [theta1, theta2] = trainLinearReg(XR, YR, R, lambda1, lambda2)

function [rate, rank, U, V] = online_train(R, U, V, X)
% X = full(mmread("X.mm.mtx"));
% X = X(1,:);
Y = full(mmread("Y.mm.mtx"));

XR = full(mmread("XR.mm.mtx"));
X = X/XR; %QR = N

if isempty(U)
    U = full(mmread("U.mm.mtx"));
end
if isempty(V)
    V = full(mmread("V.mm.mtx"));
end
% Obs = mmread("sparseN.mm.mtx");
% R = full(Obs');
% R = R(1,:);
% R = X*U*V*Y';


[m, n] = size(R);

l1=.1;
l2=.1;
iters = 100;
cost_history = zeros(iters,1);


for i = 1:iters
    
    [U] = online_update_weightsU(X, Y, R, U, V, l1);    
    [V] = online_update_weightsV(X, Y, R, U, V, l2);    
    
    cost = costFunction(X, Y, R, U, V, l1, l2);
    cost_history(i) = cost;
    if mod(i,10) == 0
        fprintf("iter: %d | cost: %d\n", i, cost);
    end
end

rate = X*U*V*Y';
[~,rank] = sort(R, 2, 'descend');
%[J, grad1, grad2] = costFunction(X, Y, R, theta1, theta2, lambda1, lambda2);

%function [J, grad1, grad2] = costFunction(X, Y, R, t1, t2, lambda1, lambda2)


