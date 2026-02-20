import React, { createContext, useContext, useState, ReactNode } from 'react';

interface EmpresaContextType {
    selectedEmpresaId: number | null;
    setSelectedEmpresaId: (id: number | null) => void;
}

const EmpresaContext = createContext<EmpresaContextType | undefined>(undefined);

export const EmpresaProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
    const [selectedEmpresaId, setSelectedEmpresaId] = useState<number | null>(null);

    return (
        <EmpresaContext.Provider value={{ selectedEmpresaId, setSelectedEmpresaId }}>
            {children}
        </EmpresaContext.Provider>
    );
};

export const useEmpresa = (): EmpresaContextType => {
    const context = useContext(EmpresaContext);
    if (context === undefined) {
        throw new Error('useEmpresa must be used within an EmpresaProvider');
    }
    return context;
};
