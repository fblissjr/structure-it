import { Landmark, ShieldCheck, Database, Settings } from 'lucide-react';

export type AppID = 'citizen' | 'compliance' | 'data';

export const Sidebar = ({ activeApp, onSwitch }: { activeApp: AppID, onSwitch: (id: AppID) => void }) => {
    const NavItem = ({ id, icon: Icon, label, color }: any) => (
        <button
            onClick={() => onSwitch(id)}
            className={`
                w-12 h-12 rounded-xl flex items-center justify-center transition-all duration-300 mb-4 group relative
                ${activeApp === id ? `bg-${color}-500/20 text-${color}-400` : 'text-slate-500 hover:bg-white/5 hover:text-slate-300'}
            `}
        >
            <Icon className="w-6 h-6" />
            {/* Tooltip */}
            <span className="absolute left-14 bg-slate-900 text-white text-xs px-2 py-1 rounded opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap border border-white/10 z-50 pointer-events-none">
                {label}
            </span>
            {/* Active Indicator Bar */}
            {activeApp === id && (
                <div className={`absolute left-0 top-2 bottom-2 w-1 rounded-r-full bg-${color}-500`} />
            )}
        </button>
    );

    return (
        <div className="w-20 h-full border-r border-white/5 flex flex-col items-center py-6 bg-slate-900/50 z-40">
            <div className="mb-8">
                <div className="w-10 h-10 bg-gradient-to-br from-violet-500 to-cyan-500 rounded-lg shadow-lg" />
            </div>

            <nav className="flex-1 flex flex-col w-full items-center">
                <NavItem id="citizen" icon={Landmark} label="Citizen Explorer" color="cyan" />
                <NavItem id="compliance" icon={ShieldCheck} label="Compliance Monitor" color="violet" />
                <div className="h-px w-8 bg-white/10 my-4" />
                <NavItem id="data" icon={Database} label="Data Sources" color="slate" />
            </nav>

            <button className="text-slate-600 hover:text-slate-400 p-3">
                <Settings className="w-5 h-5" />
            </button>
        </div>
    );
}
