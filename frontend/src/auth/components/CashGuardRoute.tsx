import { useState, useEffect } from "react";
import * as userService from "../services/userService";
import { useNavigate } from "react-router-dom";
import { getCashes, getOpenCash } from "../../services/cashService";
import NotAccess from "./NotAccess";
import NoCashAssigned from "./NoCashAssigned";
import type { User } from "../types/user";

interface CashGuardRouteProps {
  requireOpen?: boolean;
  requireClosed?: boolean;
  children: React.ReactNode;
}

export const CashGuardRoute: React.FC<CashGuardRouteProps> = ({ requireOpen, requireClosed, children }) => {
  const [allowed, setAllowed] = useState<boolean | null>(null);
  const [hasCashAssigned, setHasCashAssigned] = useState<boolean>(true);
  const [user, setUser] = useState<User | null>(null);
  const navigate = useNavigate();

  useEffect(() => {
    const check = async () => {
      try {
        const currentUser = await userService.getCurrentUser();
        setUser(currentUser);

        const cashes = await getCashes();
        const hasCaja = cashes.length > 0;

        // Si no tiene caja asignada, mostrar vista de sin caja
        if (!hasCaja) {
          console.log("❌ Usuario sin caja asignada");
          setHasCashAssigned(false);
          setAllowed(false);
          return;
        }

        console.log("✅ Usuario tiene caja asignada:", cashes);

        const openCash = await getOpenCash();
        const isOpen = !!openCash;

        if (requireOpen && !isOpen) {
          navigate("/sale-point/open-cash", { replace: true });
          return;
        }

        if (requireClosed && isOpen) {
          navigate("/sale-point/", { replace: true });
          return;
        }

        setAllowed(true);
      } catch (error) {
        console.error("❌ Error verificando caja:", error);
        setAllowed(false);
      }
    };

    check();
  }, [requireOpen, requireClosed, navigate]);

  // Mientras carga
  if (allowed === null) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  // Si no tiene caja asignada
  if (!hasCashAssigned && user) {
    return <NoCashAssigned user={user} />;
  }

  // Si no tiene acceso por otras razones
  if (!allowed && user) {
    return <NotAccess user={user} />;
  }

  // Si tiene acceso
  return <>{children}</>;
};