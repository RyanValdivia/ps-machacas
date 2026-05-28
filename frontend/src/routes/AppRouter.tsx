import Sidebar from "../components/Sidebar/Sidebar";
import Login from "../pages/Login/Login";
import ProtectedRoute from "../auth/components/ProtectedRoute";
import { Navigate, Route, BrowserRouter, Routes, useLocation } from "react-router-dom";
import { useAuth } from "../auth/hooks/useAuth";
import { lazy, Suspense, useEffect, useState } from "react";
import Users from "../pages/Settings/Components/UserManagement/Users";
import SupplierPage from "../pages/Settings/Components/SupplierManagement/Supplier";
import { CashGuardRoute } from "../auth/components/CashGuardRoute";
import Cash from "../pages/Settings/Components/CashManagement/Cash";
import General from "../pages/Settings/Components/GeneralManagement/General";


//  Lazy imports para módulos pesados
const Dashboard = lazy(() => import('../pages/Dashboard/Dashboard'));
const Inventory = lazy(() => import('../pages/Inventory/Inventory'));
const Sales = lazy(() => import('../pages/Sales/Sales'));
const Prescriptions = lazy(() => import('../pages/Prescriptions/Prescriptions'));
const Reports = lazy(() => import('../pages/Reports/Reports'));
const CashReports = lazy(() => import('../pages/Reports/components/CashReports'));
const Settings = lazy(() => import('../pages/Settings/Settings'));
const CloseCash = lazy(() => import('../pages/Sale-Point/Components/Cash/CloseCash'));
const SalePoint = lazy(() => import('../pages/Sale-Point/Components/SalePoint/SalePoint'));
const SalePointBase = lazy(() => import('../pages/Sale-Point/SalePoint'));
const OpenCash = lazy(() => import('../pages/Sale-Point/Components/Cash/OpenCash'));


function AppContent() {
    const location = useLocation();
    const { user: authUser, loading } = useAuth(); //  Hook que maneja localStorage y sucursal
    const [user, setUser] = useState(authUser);     //  Estado local sincronizado con authUser

    const isLoginRoute = location.pathname === '/';

    useEffect(() => { //Punto critico para que sesion siga iniciada y siempre se recargue AuthUser
        setUser(authUser);
    }, [authUser]);

    // Mientras carga, muestra loading
    if (loading) {
        return (
            <div className="flex items-center justify-center h-screen">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
            </div>
        );
    }

    // Si no hay usuario y no está en login, redirecciona
    if (!user && !isLoginRoute) {
        return (
            <Routes>
                <Route path="*" element={<Login onLoginSuccess={setUser} />} />
            </Routes>
        );
    }

    // Si hay usuario y está en login, muestra dashboard
    if (user && isLoginRoute) {

        return <Navigate to="/dashboard" replace />;

    }

    if (isLoginRoute) {
        return (
            <Routes>
                <Route path="/" element={<Login onLoginSuccess={setUser} />} />
            </Routes>
        );
    }

    return (
        <div className="flex h-screen overflow-hidden">
            {/* Sidebar fijo */}
            <div className="w-64 h-screen fixed top-0 left-0 bg-white shadow">
                <Sidebar />
            </div>
            <div className="flex-1 ml-64 overflow-y-auto">
                <Suspense fallback={<div className="p-6">Cargando módulo...</div>}>
                    <Routes>
                        <Route
                            path="/dashboard"
                            element={
                                <ProtectedRoute user={user} allowedLevels={[0, 1, 2, 3, 4]}>
                                    <Dashboard />
                                </ProtectedRoute>
                            }
                        />

                        <Route path="/sale-point" element={
                            //<ProtectedRoute user={user} allowedLevels={[1,2]}>
                                <SalePointBase key={location.key} />
                            //</ProtectedRoute>
                            } >
                            {/* SalePointBase maneja rutas hijas */}
                            <Route path="" element={
                                <CashGuardRoute requireOpen>
                                <SalePoint />
                                </CashGuardRoute>
                            } />
                            <Route path="open-cash" element={
                                <CashGuardRoute requireClosed >
                                <OpenCash />
                                </CashGuardRoute>
                            } />
                            <Route path="close-cash" element={
                                <CashGuardRoute requireOpen>
                                <CloseCash />
                                </CashGuardRoute>
                            } />
                        </Route>

                        <Route path="/sales" element={
                            <ProtectedRoute user={user} allowedLevels={[0, 1, 2]}>
                                <Sales />
                            </ProtectedRoute>
                        } />

                        <Route path="/inventory" element={
                            <ProtectedRoute user={user} allowedLevels={[0, 1, 3]}>
                                <Inventory />
                            </ProtectedRoute>
                        } />

                        <Route path="/prescriptions" element={
                            <ProtectedRoute user={user} allowedLevels={[0, 1, 4]}>
                                <Prescriptions />
                            </ProtectedRoute>
                        } />


                        <Route path="/reports" element={
                            <ProtectedRoute user={user} allowedLevels={[0, 1]}>
                                <Reports />
                            </ProtectedRoute>
                        } />

                        <Route path="/reports/cash" element={
                            <ProtectedRoute user={user} allowedLevels={[0, 1]}>
                                <CashReports />
                            </ProtectedRoute>
                        } />
                        <Route path="/settings" element={
                                <ProtectedRoute user={user} allowedLevels={[0, 1]}>
                                <Settings /> {/* <Outlet /> */}
                                </ProtectedRoute>
                            }>
                            <Route path="" element={<General />} />
                            <Route path="supliers" element={
                                <ProtectedRoute user={user} allowedLevels={[0, 1]}>
                                <SupplierPage />
                                </ProtectedRoute>
                            } />

                            <Route path="users" element={
                                <ProtectedRoute user={user} allowedLevels={[0, 1]}>
                                <Users />
                                </ProtectedRoute>
                            } />
                            <Route path="cash" element={
                                <ProtectedRoute user={user} allowedLevels={[0, 1]}>
                                <Cash />
                                </ProtectedRoute>
                            } />
                            </Route>
                    </Routes>
                </Suspense>
            </div>
        </div>
    );
}

export default function AppRouter() {
    return (
        <BrowserRouter>
            <AppContent />
        </BrowserRouter>
    );
}