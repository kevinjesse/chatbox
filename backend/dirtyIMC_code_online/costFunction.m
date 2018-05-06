function [J] = costFunction(X, Y, R, U, V, lambda1, lambda2)
% U is U
% V is V
% Linear Regression
h = X*U*V*Y';
% U(1) = 0;
% V(1) = 0;
J = mean(sum((h-R).^2,2)) + lambda1*(norm(U).^2) + lambda2*(norm(V).^2);
% grad1 = 2*X*(h-R)*Y'*V + lambda1*U;
% grad2 = 2*U'*X*(h-R)*Y'+ lambda2*V;
% 
% grad1 = grad1(:);
% grad2 = grad2(:);

end
